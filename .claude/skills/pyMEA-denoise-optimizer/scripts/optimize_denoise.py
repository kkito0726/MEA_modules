#!/usr/bin/env python3
"""MEA計測データの最適ノイズ除去条件を探索する。

.hed パスを受け取り、信号特性を解析して細胞種(心筋/神経)を自動推定し、
候補手法(プリセット + パラメータ微調整)を適用して S/N 比・ノイズ低減・
振幅保持・検出維持を比較し、最適条件を推奨レポートとして出力する。

デノイズ手法は scipy / pywt で自前実装しているため、pyMEA 側のデノイズ
メソッド(MEA.highpass 等)が未実装の環境でも動作する。読み込みのみ
read_MEA を使う。出力の「pyMEAでの適用方法」は最終的にライブラリの
プリセット/メソッドで再現できる形にしてある。

使い方:
    python optimize_denoise.py --hed path/to.hed [--start 0 --end 5
        --distance 450 --cell-type auto --json]
"""

import argparse
import json
import sys

import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

try:
    import pywt

    HAS_PYWT = True
except ImportError:
    HAS_PYWT = False

from pyMEA import detect_peak_neg, read_MEA

NUM_CH = 64


# --------------------------------------------------------------------------
# デノイズ手法(ライブラリ非依存・自前実装)
# --------------------------------------------------------------------------
def highpass(sig, cutoff, sr, order=4):
    sos = butter(order, cutoff, btype="highpass", fs=sr, output="sos")
    return sosfiltfilt(sos, sig)


def bandpass(sig, low, high, sr, order=4):
    sos = butter(order, [low, high], btype="bandpass", fs=sr, output="sos")
    return sosfiltfilt(sos, sig)


def wavelet_denoise(sig, wavelet="db4", max_level=6):
    sig = np.array(sig, dtype=float)
    level = min(pywt.dwt_max_level(len(sig), pywt.Wavelet(wavelet).dec_len), max_level)
    coeffs = pywt.wavedec(sig, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    uthresh = sigma * np.sqrt(2 * np.log(len(sig)))
    coeffs[1:] = [pywt.threshold(c, uthresh, mode="soft") for c in coeffs[1:]]
    return pywt.waverec(coeffs, wavelet)[: len(sig)]


def apply_method(arr, spec, sr):
    """spec で指定された手法を全電極(1..64)に適用した配列を返す(時刻行は保持)。"""
    out = arr.copy()
    median_ref = np.median(arr[1 : NUM_CH + 1], axis=0)
    for ch in range(1, NUM_CH + 1):
        sig = arr[ch]
        if spec.get("cmr"):
            sig = sig - median_ref
        band = spec.get("band")
        if band == "highpass":
            sig = highpass(sig, spec["low"], sr)
        elif band == "bandpass":
            sig = bandpass(sig, spec["low"], spec["high"], sr)
        if spec.get("wavelet"):
            sig = wavelet_denoise(sig)
        out[ch] = sig
    return out


# --------------------------------------------------------------------------
# 信号特性の解析・細胞種の自動推定
# --------------------------------------------------------------------------
def band_power(sig, sr, lo, hi):
    f, pxx = welch(sig, fs=sr, nperseg=min(4096, len(sig)))
    return pxx[(f >= lo) & (f < hi)].sum()


# --------------------------------------------------------------------------
# S/N 比・検出評価
# --------------------------------------------------------------------------
def snr(sig, spikes, sr, halfwin_ms=15, ampwin_ms=3):
    h = int(halfwin_ms * sr / 1000)
    aw = int(ampwin_ms * sr / 1000)
    mask = np.zeros(len(sig), bool)
    for p in spikes:
        mask[max(0, p - h) : p + h] = True
    if not (~mask).any():
        return np.nan
    noise = sig[~mask].std()
    amps = [
        abs(sig[max(0, p - aw) : p + aw].min() - np.median(sig[max(0, p - h) : p + h]))
        for p in spikes
        if len(sig[max(0, p - aw) : p + aw])
    ]
    return (np.median(amps) / noise) if amps and noise > 0 else np.nan


# --------------------------------------------------------------------------
# 候補手法の定義(細胞種別: プリセット + パラメータ微調整)
# --------------------------------------------------------------------------
def candidates(cell_type):
    if cell_type == "cardio":
        return [
            ("raw", {}, "FilterType.NONE"),
            ("highpass(1)+CMR", {"band": "highpass", "low": 1, "cmr": True},
             "FilterType.CARDIO_DENOISE"),
            ("bandpass(1-1000)+CMR", {"band": "bandpass", "low": 1, "high": 1000, "cmr": True},
             "FilterType.CARDIO_DENOISE_WEAK"),
            ("bandpass(1-500)+CMR", {"band": "bandpass", "low": 1, "high": 500, "cmr": True},
             "mea.data.bandpass(1, 500).common_median_reference()"),
            ("bandpass(1-2000)+CMR", {"band": "bandpass", "low": 1, "high": 2000, "cmr": True},
             "mea.data.bandpass(1, 2000).common_median_reference()"),
            ("wavelet", {"wavelet": True}, "mea.data.wavelet_denoise()"),
            ("highpass(1)", {"band": "highpass", "low": 1}, "mea.data.highpass(1)"),
        ]
    return [
        ("raw", {}, "FilterType.NONE"),
        ("bandpass(100-3000)", {"band": "bandpass", "low": 100, "high": 3000},
         "FilterType.NEURO_DENOISE"),
        ("bandpass(300-3000)", {"band": "bandpass", "low": 300, "high": 3000},
         "mea.data.bandpass(300, 3000)"),
        ("bandpass(150-3000)", {"band": "bandpass", "low": 150, "high": 3000},
         "mea.data.bandpass(150, 3000)"),
        ("bandpass(100-3000)+CMR", {"band": "bandpass", "low": 100, "high": 3000, "cmr": True},
         "mea.data.common_median_reference().bandpass(100, 3000)"),
        ("bandpass(100-3000)+wavelet", {"band": "bandpass", "low": 100, "high": 3000, "wavelet": True},
         "mea.data.bandpass(100, 3000).wavelet_denoise()"),
    ]


# --------------------------------------------------------------------------
# メイン
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hed", required=True, help=".hedファイルのパス")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=5)
    ap.add_argument("--distance", type=int, default=450, help="電極間距離(μm)")
    ap.add_argument("--cell-type", choices=["auto", "cardio", "neuro"], default="auto")
    ap.add_argument("--top-ch", type=int, default=8, help="評価に使う良好chの数")
    ap.add_argument("--json", action="store_true", help="JSONも出力する")
    args = ap.parse_args()

    mea = read_MEA(args.hed, args.start, args.end, args.distance)
    sr = mea.data.SAMPLING_RATE
    arr = np.array([mea.data.array[ch].copy() for ch in range(NUM_CH + 1)])

    # 確実な実スパイク(高閾値)= グラウンドトゥルース
    gt = detect_peak_neg(mea.data, threshold=4)
    counts = [len(np.asarray(gt[ch])) for ch in range(1, NUM_CH + 1)]
    best_ch = int(np.argmax(counts)) + 1
    sig = arr[best_ch]
    total = band_power(sig, sr, 0, sr / 2) or 1.0
    p_low = band_power(sig, sr, 1, 300)
    p_high = band_power(sig, sr, 300, 3000)
    p_mains = band_power(sig, sr, 50, 60)
    auto_type = "neuro" if p_high > p_low else "cardio"
    cell_type = auto_type if args.cell_type == "auto" else args.cell_type

    char = {
        "sampling_rate": int(sr),
        "auto_cell_type": auto_type,
        "used_cell_type": cell_type,
        "max_peaks": int(max(counts)),
        "channels_with_signal": int(sum(c >= 3 for c in counts)),
        "rms_best_ch": round(float(sig.std()), 1),
        "band_pct": {
            "1-300Hz": round(100 * p_low / total),
            "300-3000Hz": round(100 * p_high / total),
            "50-60Hz(mains)": round(100 * p_mains / total),
        },
    }

    eval_chs = sorted(
        [ch for ch in range(1, NUM_CH + 1) if counts[ch - 1] >= 3],
        key=lambda c: -counts[c - 1],
    )[: args.top_ch]
    if not eval_chs:
        print("[警告] ピークが十分に検出できる電極がありません。start/end や閾値を見直してください。")
        sys.exit(1)
    tol = int(0.004 * sr)

    results = []
    raw_snr = raw_amp = None
    for name, spec, apply_str in candidates(cell_type):
        if spec.get("wavelet") and not HAS_PYWT:
            continue
        out = apply_method(arr, spec, sr) if spec else arr
        out[0] = arr[0]
        from pyMEA.domain.model.MEA import MEA

        out_mea = MEA(mea.data.hed_path, args.start, args.end, sr, mea.data.GAIN, out)
        det = detect_peak_neg(out_mea, threshold=3)

        snrs, rmss, amps, covs, gtot = [], [], [], 0, 0
        for ch in eval_chs:
            sp = np.asarray(gt[ch])
            snrs.append(snr(out[ch], sp, sr))
            h = int(0.015 * sr)
            mask = np.zeros(len(out[ch]), bool)
            for p in sp:
                mask[max(0, p - h) : p + h] = True
            rmss.append(out[ch][~mask].std())
            amps.append(np.median([abs(out[ch][max(0, p - 30) : p + 30].min()) for p in sp]))
            d = np.asarray(det[ch])
            gtot += len(sp)
            for x in sp:
                if len(d) and np.min(np.abs(d - x)) <= tol:
                    covs += 1
        S = float(np.nanmedian(snrs))
        R = float(np.nanmedian(rmss))
        A = float(np.nanmedian(amps))
        cov = 100 * covs / gtot if gtot else 0
        if name == "raw":
            raw_snr, raw_amp, raw_rms = S, A, R
        results.append(
            {
                "method": name,
                "apply": apply_str,
                "snr": round(S, 1),
                "improvement": round(S / raw_snr, 2) if raw_snr else 1.0,
                "noise_rms_pct": round(100 * R / raw_rms) if raw_snr else 100,
                "amp_keep_pct": round(100 * A / raw_amp) if raw_amp else 100,
                "detection_pct": round(cov),
            }
        )

    # 推奨ロジック:
    #   弱信号では detect_peak が相対閾値(×SD)で動くため検出維持率が交絡する。
    #   そこで「振幅保持(スパイク形状を壊していないか)」を主ゲートにし、
    #   振幅を保てている手法の中で最大S/Nを推奨する(過剰デノイズを避ける)。
    non_raw = [r for r in results if r["method"] != "raw"]
    safe = [r for r in non_raw if r["amp_keep_pct"] >= 80]
    pool = safe if safe else non_raw
    recommended = max(pool, key=lambda r: r["snr"]) if pool else results[0]

    # 振幅を犠牲にしてでもS/Nを最大化したい場合の別案(検出より可視化優先など)
    aggressive = max(non_raw, key=lambda r: r["snr"]) if non_raw else None
    if aggressive is recommended:
        aggressive = None

    report = {
        "characterization": char,
        "comparison": results,
        "recommended": recommended,
        "aggressive_option": aggressive,
    }

    # ---- 人間向けレポート ----
    print("=" * 64)
    print("MEA ノイズ除去 最適条件 探索レポート")
    print("=" * 64)
    print(f"\n■ 信号特性")
    print(f"  サンプリングレート : {char['sampling_rate']} Hz")
    print(f"  自動判定の細胞種   : {char['auto_cell_type']}  (採用: {char['used_cell_type']})")
    print(f"  信号良好な電極数   : {char['channels_with_signal']} / 64  (最大ピーク数 {char['max_peaks']})")
    print(f"  ベースラインRMS    : {char['rms_best_ch']} μV")
    print(f"  帯域パワー%        : {char['band_pct']}")
    print(f"\n■ 手法比較 (評価ch={eval_chs})")
    print(f"  {'手法':<26}{'S/N':>6}{'改善x':>7}{'ノイズ':>7}{'振幅':>7}{'検出%':>7}")
    for r in results:
        mark = " ★" if r is recommended else ""
        print(
            f"  {r['method']:<26}{r['snr']:>6.1f}{r['improvement']:>7.2f}"
            f"{r['noise_rms_pct']:>6}%{r['amp_keep_pct']:>6}%{r['detection_pct']:>6}%{mark}"
        )
    print(f"\n■ 推奨条件: {recommended['method']}")
    print(f"  S/N {recommended['snr']} (raw比 {recommended['improvement']}x) / "
          f"振幅保持 {recommended['amp_keep_pct']}% / 検出維持 {recommended['detection_pct']}%")
    print(f"  pyMEAでの適用: {recommended['apply']}")
    if aggressive:
        print(f"\n■ 別案(S/N最大・振幅は犠牲): {aggressive['method']}")
        print(f"  S/N {aggressive['snr']} (raw比 {aggressive['improvement']}x) / "
              f"振幅保持 {aggressive['amp_keep_pct']}%")
        print(f"  pyMEAでの適用: {aggressive['apply']}")
        print("  ※ 振幅(スパイク形状)を削るため、検出より可視化を優先する場合のみ。")
    print("\n  [注] 検出維持%は detect_peak の相対閾値の影響で弱信号では参考値。")
    print("       推奨は振幅保持(スパイク形状を壊さないか)を主基準に選んでいます。")
    if not HAS_PYWT:
        print("  [注] PyWavelets 未導入のため wavelet 系は評価から除外しました。")

    if args.json:
        print("\n" + "=" * 64 + "\nJSON\n" + "=" * 64)
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
