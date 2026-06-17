"""テスト用フィクスチャ .npz を read_MEA_npz 形式へ変換する開発用スクリプト。

`test/resources/fixtures/{cardio,neuro}.npz` を `PyMEA#save_npz`(= read_MEA_npz)
で読める正規形式へ上書き保存する。入力は旧独自形式(キー array/SAMPLING_RATE/GAIN)
でも、既に変換済みの新形式でも受け付ける(float32 は無損失なので dtype 切替に再利用可)。

使い方:
    python test/tools/convert_fixtures.py --dtype float32
    python test/tools/convert_fixtures.py --dtype int16
"""

import argparse
from pathlib import Path

import numpy as np

from pyMEA import read_MEA_npz
from pyMEA.domain.model.HedPath import HedPath
from pyMEA.domain.model.MEA import MEA
from pyMEA.infrastructure.npz_io import KEY_VOLTAGES, save_mea_npz

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "resources" / "fixtures"
FIXTURES = ("cardio", "neuro")
ELECTRODE_DISTANCE = 450
START, END = 0, 3


def _load_mea(path: Path, name: str) -> MEA:
    """旧形式(array/SAMPLING_RATE/GAIN) / 新形式(voltages...) いずれからも MEA を得る。"""
    with np.load(path, allow_pickle=True) as data:
        if KEY_VOLTAGES in data.files:
            # 既に新形式 → read_MEA_npz 経由で MEA を復元(float32 は無損失)
            return read_MEA_npz(str(path)).data
        array = np.asarray(data["array"], dtype=np.float64)
        sampling_rate = int(data["SAMPLING_RATE"])
        gain = int(data["GAIN"])
    return MEA(HedPath(f"{name}.hed"), START, END, sampling_rate, gain, array)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dtype", choices=("float32", "int16"), default="float32",
        help="保存 dtype (既定: float32, 電位ビット一致)",
    )
    args = parser.parse_args()

    for name in FIXTURES:
        path = FIXTURE_DIR / f"{name}.npz"
        mea = _load_mea(path, name)
        save_mea_npz(mea, str(path), args.dtype, ELECTRODE_DISTANCE)
        size_kb = path.stat().st_size / 1024
        print(f"{name}: {args.dtype:8} shape={mea.shape} -> {path} ({size_kb:.0f}KB)")


if __name__ == "__main__":
    main()
