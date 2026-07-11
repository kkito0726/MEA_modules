# ノイズ除去 (S/N比改善) の使い方

MEA計測データのノイズを除去し、S/N比を改善するための機能。ピーク検出・ISI・FPD・伝導速度の算出精度を上げたいときに使う。

すべての手法は**全時系列を保持**し (shape `(65, N)` のまま)、**ゼロ位相**なのでピークタイミングをずらさない。また[イミュータブル設計](../../CLAUDE.md)に従い、元データを変更せず新しいインスタンスを返す。

> 設計の背景・実測データは [PRD: ノイズ除去 / SN比改善機能](../prd/denoising.md) を参照。

---

## 目次

- [クイックスタート](#クイックスタート)
- [手法の選び方](#手法の選び方)
- [プリセット](#プリセット)
- [個別メソッド](#個別メソッド)
- [独自パイプラインを組む](#独自パイプラインを組む)
- [S/N比で手法を検証する](#sn比で手法を検証する)
- [既存フィルターとの使い分け](#既存フィルターとの使い分け)
- [注意点・制約](#注意点制約)

---

## クイックスタート

`read_MEA` に `filter_type` を渡すだけでデノイズが適用される。返り値は通常どおり `PyMEA` なので、以降の解析は普段と同じ。

```python
from pyMEA import *

hed_path = "/User/you/your_record_data.hed"
start, end = 0, 5
electrode_distance = 450

# 心筋データのデノイズ
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.CARDIO_DENOISE)

# 以降は通常どおり
peak_index = detect_peak_neg(mea.data)
isi = mea.calculator.isi(peak_index, ch=6)
mea.fig.showAll()
```

---

## 手法の選び方

**最適な手法は細胞種と信号強度で変わる**。単一の万能手法は存在しない。まず下表で当たりをつけ、[S/N比](#sn比で手法を検証する)で確認する。

| 細胞種 | 信号強度 | 推奨 | 理由 |
|---|---|---|---|
| 心筋 | 強〜中 | `CARDIO_DENOISE` | ドリフト除去 + 共通モード除去。振幅を歪めない |
| 心筋 | 微弱 | `CARDIO_DENOISE_WEAK` | 支配ノイズが帯域外の広帯域ノイズになるため bandpass が要る |
| 神経 | — | `NEURO_DENOISE` | スパイク帯 (100-3000Hz) のみ通す |

信号強度の目安は `Calculator.snr` の値。心筋でおおむね S/N が 10 を下回るなら「微弱」側の `CARDIO_DENOISE_WEAK` を検討する。

---

## プリセット

`FilterType` の3つがデノイズ用プリセット。いずれも `read_MEA` の第5引数に渡す。

| プリセット | 適用される処理 | 対象 |
|---|---|---|
| `FilterType.CARDIO_DENOISE` | `highpass(1)` → `common_median_reference()` | 心筋 (強〜中信号) |
| `FilterType.CARDIO_DENOISE_WEAK` | `bandpass(1, 1000)` → `common_median_reference()` | 微弱な心筋 |
| `FilterType.NEURO_DENOISE` | `bandpass(100, 3000)` | 神経 |

```python
# 心筋 (強〜中信号): ドリフト除去 + 共通モードノイズ除去
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.CARDIO_DENOISE)

# 微弱な心筋: 帯域通過 + 共通モードノイズ除去
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.CARDIO_DENOISE_WEAK)

# 神経: スパイク帯(100-3000Hz)のみ通過
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.NEURO_DENOISE)
```

### 実測の効果 (PRDの検証結果より)

| データ | 手法 | S/N改善 | 振幅保持 | 検出 |
|---|---|---|---|---|
| 心筋 (強信号) | `CARDIO_DENOISE` 相当 | 1.23x | 102% | 100%・タイミングズレ 0ms |
| 心筋 (微弱, S/N≈6.6) | `CARDIO_DENOISE_WEAK` 相当 | 1.7x | — | 真検出率 95%→100%・誤検出 23%→8% |
| 神経 (弱信号) | `NEURO_DENOISE` 相当 | 1.16x | 92% | — |

---

## 個別メソッド

いずれも `PyMEA` (`mea`) と `MEA` (`mea.data`) の両方にあるメソッド。`mea.xxx()` は `PyMEA` を返し (`fig`・`calculator` が追従)、`mea.data.xxx()` は `MEA` を返す。どちらもメソッドチェーンで合成できる。以下の例は `mea.data` 側で示すが、`mea` 側でも同じ引数で呼べる。

### `highpass(cutoff=1, order=4)`

ベースラインドリフト (低周波) を除去する。ゼロ位相 Butterworth。

```python
denoised = mea.data.highpass(cutoff=1)
```

- **対象ノイズ**: ベースラインドリフト
- **長所**: ピークタイミングが不変。軽量
- **用途**: 心筋の前処理の定番

### `bandpass(low, high, order=4)`

指定した周波数帯のみ通す。ゼロ位相 Butterworth。

```python
denoised = mea.data.bandpass(low=100, high=3000)   # 神経のスパイク帯
denoised = mea.data.bandpass(low=1, high=1000)     # 心筋 (鋭いスパイクを保持)
```

- **対象ノイズ**: ドリフト + 信号帯域外の広帯域ノイズ
- **帯域の目安**: 心筋 `1-1000Hz` / 神経 `100-3000Hz`
- **⚠ 心筋で `bandpass(1, 300)` は禁物**。鋭い脱分極スパイクを潰し、振幅が49%まで落ちる (実測)

### `common_median_reference()`

各時刻で全64電極の**中央値**を求め、各電極から減算する (CMR)。64chの空間冗長性を使い、電極間で相関するノイズを消す。

```python
denoised = mea.data.common_median_reference()
```

- **対象ノイズ**: 電源ハム、参照電極ドリフト、機械振動などの**共通モードノイズ**
- **長所**: スパイク形状を変えない (無歪み)。パラメータ不要
- **注意**: 電極間で無相関な熱雑音には無効。**神経データでは共通モード成分が少なく効果が薄い** (実測 S/N 1.02x)
- 平均 (CAR) でなく中央値を使うのは、心筋の同期拍動で信号成分を引きすぎないため

### `wavelet_denoise(wavelet="db4", level=None)`

離散ウェーブレット変換 + ソフト閾値で、信号帯域内に重なる広帯域ノイズを除去する。閾値はノイズ標準偏差から自動算出 (universal threshold)。

```python
denoised = mea.data.wavelet_denoise(wavelet="db4")
denoised = mea.data.wavelet_denoise(wavelet="db4", level=5)  # 分解レベル指定
```

- **対象ノイズ**: 信号帯域内の広帯域 (白色) ノイズ
- **長所**: 線形フィルタと違い、鋭いスパイク形状を保ったまま帯域内ノイズを落とす。**強信号の心筋では単独で最もS/Nが上がる**
- **⚠ 微弱信号では弱いスパイクごと削るリスク**。微弱心筋で真検出率が 84% に低下した実測があり、プリセットには含めていない。使うなら必ず[S/N比と検出数を確認](#sn比で手法を検証する)する
- `level=None` のとき信号長から自動決定 (上限6)
- 依存: PyWavelets

---

## 独自パイプラインを組む

プリセットを使わず、メソッドを直接合成して独自のパイプラインを組める。**`PyMEA` (`mea`) のメソッドとして呼ぶ**のが基本。デノイズ後のデータで再構築した `PyMEA` を返すので、`fig` / `calculator` もそのまま使える。

```python
mea = read_MEA(hed_path, start, end, electrode_distance)  # フィルターなしで読み込む

# PyMEA を返す → fig・calculator もデノイズ後データに追従する
denoised = mea.bandpass(1, 1000).common_median_reference()

peak_index = detect_peak_neg(denoised.data)
snr = denoised.calculator.snr(peak_index, ch=6)
isi = denoised.calculator.isi(peak_index, ch=6)
denoised.fig.showAll()
```

`PyMEA` から使えるデノイズメソッドは `highpass` / `bandpass` / `common_median_reference` / `wavelet_denoise` の4つ。いずれも新しい `PyMEA` を返し、ゼロ位相でピークタイミングを変えない。

### ⚠ 注意: `mea.data.xxx()` は `MEA` を返す (fig / calculator は付いてこない)

`mea.xxx()` (PyMEA) と `mea.data.xxx()` (MEA) は返すものが違う。`mea.data` を直接触ると `MEA` が返り、`fig` / `calculator` は**読み込み時のデータに束縛されたまま**になる。

```python
denoised = mea.data.wavelet_denoise()   # ← MEA を返す (PyMEA ではない)
peak_index = detect_peak_neg(denoised)

# ❌ 間違い: mea.calculator は生データを持っているので、生データのS/N比が返る
snr = mea.calculator.snr(peak_index, ch=6)
```

**基本は `mea.data` でなく `mea` のメソッドを使う**。そうすれば `fig` / `calculator` の組み直しは不要。

```python
# ✅ PyMEA のメソッドを使えば calculator も自動で追従する
denoised = mea.bandpass(1, 1000).common_median_reference()
snr = denoised.calculator.snr(detect_peak_neg(denoised.data), ch=6)
```

どうしても `MEA` (`mea.data`) を直接扱った場合は、`Calculator` / `FigMEA` を手で組み直す。

```python
from pyMEA import Calculator, FigMEA

denoised = mea.data.bandpass(1, 1000).common_median_reference()  # MEA
calc = Calculator(denoised, mea.electrode.ele_dis)
fig = FigMEA(denoised, mea.electrode)
```

---

## S/N比で手法を検証する

`Calculator.snr` は `スパイク振幅 / 静穏区間のノイズRMS` を返す。**最適手法はデータ次第なので、自分のデータで比較して選ぶ**のが前提の設計になっている。

```python
def snr(peak_index: Peaks64, ch: int, noise_window: float = 0.015) -> float
```

- `noise_window`: 各スパイクの前後でノイズ計算から除外する片側幅 (s)。既定 ±15ms

### 手法を比較する

生データと各プリセットのS/N比を並べて、自分のデータで最良の手法を選ぶ。

```python
from pyMEA import FilterType, detect_peak_neg, read_MEA

ch = 6
args = (hed_path, start, end, electrode_distance)

for name, filter_type in [
    ("raw", FilterType.NONE),
    ("cardio_denoise", FilterType.CARDIO_DENOISE),
    ("cardio_denoise_weak", FilterType.CARDIO_DENOISE_WEAK),
]:
    mea = read_MEA(*args, filter_type)
    peak_index = detect_peak_neg(mea.data)
    snr = mea.calculator.snr(peak_index, ch=ch)
    print(f"{name:20s} S/N={snr:6.2f}  検出数={len(peak_index[ch])}")
```

**S/N比だけで判断しない。検出数も必ず見る。** wavelet のようにノイズと一緒に弱いスパイクを削る手法は、S/N比が上がっても検出を取りこぼしていることがある。

神経データは正解ラベルが無く相対閾値検出が交絡するため、最終的には波形の目視確認で帯域・閾値を調整することを推奨する。

---

## 既存フィルターとの使い分け

デノイズ機能は既存フィルターの**置き換えではなく併存**。目的が異なる。

| 機能 | 時系列 | 目的 | 対象ノイズ |
|---|---|---|---|
| `CARDIO_DENOISE` / `_WEAK` / `NEURO_DENOISE` | **保持** | S/N比改善 | ドリフト・広帯域・共通モード |
| `FilterType.CARDIO_AVE_WAVE` | **1拍に潰れる** | 平均波形の算出 | (加算平均で√N倍改善) |
| `FilterType.FILTER_MEA` | 保持 | 電源同期減算 | 電源ハムの基本波のみ |
| `MEA.iirnotch_filter(50)` | 保持 | 50Hzノッチ | 電源基本波のみ |

- **`CARDIO_AVE_WAVE` は時系列を1拍に潰す**ため、ISI・拍動間変動・不整脈が失われる。これらを解析したいならデノイズ機能を使う
- `FILTER_MEA` / `iirnotch` は電源ハム専用。ドリフトや広帯域ノイズには無効。共通モードの電源ノイズなら `common_median_reference()` のほうが広く効く

---

## 注意点・制約

### ナイキスト周波数を超える帯域は指定できない

`bandpass` / `highpass` のカットオフはサンプリングレートの半分未満でなければならない。

```python
# サンプリングレート 10000Hz の場合、上限は 5000Hz 未満
mea.data.bandpass(100, 3000)   # OK
mea.data.bandpass(100, 5000)   # ValueError: Digital filter critical frequencies must be 0 < Wn < fs/2
```

`down_sampling()` を掛けた後はサンプリングレートが下がるため、デノイズは**ダウンサンプリングの前**に適用する。

### 微弱信号での wavelet

前述のとおり、弱いスパイクごと削って検出を落とすことがある。微弱心筋では `bandpass(1, 1000) + CMR` (= `CARDIO_DENOISE_WEAK`) を使う。

### 神経データでの CMR

神経は共通モード成分が少なく、CMR の効果はほぼ無い (実測 S/N 1.02x)。`NEURO_DENOISE` に CMR が含まれないのはこのため。

### 処理時間の目安

64ch × 3秒 (10kHz, 30000フレーム) での実測値。数十秒のデータでも実用的な速度で動く。

| メソッド | 処理時間 |
|---|---|
| `highpass(1)` | 約 0.08 s |
| `bandpass(1, 1000)` | 約 0.10 s |
| `common_median_reference()` | 約 0.04 s |
| `wavelet_denoise()` | 約 0.05 s |

### 対象外

- スパイクソーティング・分類
- リアルタイム (オンライン) 処理 — バッチ解析のみ
