"""読込経路のファクトリと正規化DTO。

入力ファイルの拡張子に応じた Reader を生成し、形式差(メタ情報の出所)を吸収した
MEAReadResult を返す。新形式追加時は Reader を1つ足して create_reader に分岐を
1行追加するだけでよい(開放閉鎖原則)。
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy import float64
from numpy._typing import NDArray

from pyMEA.domain.model.HedPath import HedPath
from pyMEA.infrastructure import read_bio
from pyMEA.infrastructure.npz_io import (
    KEY_DTYPE,
    KEY_ELECTRODE_DISTANCE,
    KEY_END,
    KEY_GAIN,
    KEY_HED_PATH,
    KEY_SAMPLING_RATE,
    KEY_SCALE,
    KEY_START,
    KEY_VOLTAGES,
)


@dataclass(frozen=True)
class MEAReadResult:
    """形式差を吸収した読込結果。array は時刻行+電位の (65, N)。"""

    hed_path: HedPath
    array: NDArray[float64]
    sampling_rate: int
    gain: int
    start: float
    end: float
    # 電極間距離 (μm)。.npz は保存値を持つ。.hed/.bio は持たない(read_MEAが引数で受ける)
    electrode_distance: int | None = None


class MEAReader(Protocol):
    def read(self) -> MEAReadResult: ...


class HedBioReader:
    """.hed/.bio を読み込む Reader。サンプリングレート・GAINはヘッダーから取得する。"""

    def __init__(self, hed_path: str, start: int, end: int):
        self._hed_path = HedPath(hed_path)
        self._start = start
        self._end = end

    def read(self) -> MEAReadResult:
        # フィクスチャ差し替えが効くようモジュール経由で呼ぶ
        hed_data = read_bio.decode_hed(self._hed_path)
        array = read_bio.hed2array(self._hed_path, self._start, self._end)
        return MEAReadResult(
            hed_path=self._hed_path,
            array=array,
            sampling_rate=hed_data.SAMPLING_RATE,
            gain=hed_data.GAIN,
            start=self._start,
            end=self._end,
        )


class NpzReader:
    """.npz を読み込む Reader。時刻行はメタ情報から再生成する。"""

    def __init__(self, path: str):
        self._path = path

    def read(self) -> MEAReadResult:
        with np.load(self._path) as data:
            stored = data[KEY_VOLTAGES]
            dtype = str(data[KEY_DTYPE])
            scale = float(data[KEY_SCALE])
            sampling_rate = int(data[KEY_SAMPLING_RATE])
            gain = int(data[KEY_GAIN])
            start = float(data[KEY_START])
            end = float(data[KEY_END])
            hed_path = str(data[KEY_HED_PATH])
            # 旧形式(電極間距離なし)との後方互換のため存在チェックする
            electrode_distance = (
                int(data[KEY_ELECTRODE_DISTANCE])
                if KEY_ELECTRODE_DISTANCE in data.files
                else None
            )

        if dtype == "int16":
            voltages = stored.astype(np.float32) * np.float32(scale)
        else:
            voltages = stored.astype(np.float32)

        n = voltages.shape[1]
        # (65, N) を float32 で組み立てる。時刻行は捨て駒(MEA側で float64 再生成)。
        array = np.empty((voltages.shape[0] + 1, n), dtype=np.float32)
        array[0] = np.arange(n) / sampling_rate + start
        array[1:] = voltages

        return MEAReadResult(
            hed_path=HedPath(hed_path),
            array=array,
            sampling_rate=sampling_rate,
            gain=gain,
            start=start,
            end=end,
            electrode_distance=electrode_distance,
        )


def create_reader(
    path: str, start: int | None = None, end: int | None = None
) -> MEAReader:
    """拡張子に応じた Reader を生成する。"""
    suffix = Path(path).suffix
    if suffix == ".hed":
        return HedBioReader(path, start, end)
    if suffix == ".npz":
        return NpzReader(path)
    raise ValueError(f"未対応の拡張子です: {suffix}")
