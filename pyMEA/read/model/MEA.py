from dataclasses import dataclass
from functools import cached_property
from typing import Any

from numpy import float64, ndarray
from numpy._typing import NDArray

from pyMEA.find_peaks.peak_model import Peaks64
from pyMEA.read.model.HedPath import HedPath


@dataclass(frozen=True)
class MEA:
    """
    MEA計測データの読み込み
    ----------
    Args:
        hed_path: ヘッダーファイルのパス
        start: 読み込み開始時間 (s)
        end: 読み込み終了時間 (s)
    """

    hed_path: HedPath
    start: int
    end: int
    SAMPLING_RATE: int
    GAIN: int
    array: NDArray[float64]

    def __post_init__(self):
        self.array.setflags(write=False)
        # self.array に対して副作用を与えないようコピーして freeze
        object.__setattr__(self, 'array', self._freeze_array(self.array.copy()))

    @staticmethod
    def _freeze_array(arr) -> ndarray[Any]:
        arr.setflags(write=False)
        return arr

    @cached_property
    def time(self):
        return self.end - self.start

    def __repr__(self):
        return repr(self.array)

    def __getitem__(self, index: int) -> ndarray:
        return self.array[index]

    def __len__(self) -> int:
        return len(self.array)

    def __iter__(self):
        return iter(self.array)

    def __add__(self, value):
        return self.array + value

    def __sub__(self, value):
        return self.array - value

    def __mul__(self, value):
        return self.array * value

    def __truediv__(self, value):
        return self.array / value

    def __floordiv__(self, value):
        return self.array // value

    @property
    def info(self) -> str:
        info = (
            f"読み込み開始時間  : {self.start} s\n"
            f"読み込み終了時間  : {self.end} s\n"
            f"読み込み合計時間  : {self.time} s\n"
            f"サンプリングレート: {self.SAMPLING_RATE} Hz\n"
            f"GAIN           : {self.GAIN}"
        )
        print(info)
        return info

    @property
    def shape(self) -> tuple[int, ...]:
        return self.array.shape

    def from_slice(self, start_frame: int | float, end_frame: int | float):
        return MEA(
            self.hed_path,
            self.start,
            self.end,
            self.SAMPLING_RATE,
            self.GAIN,
            self.array[:, int(start_frame) : int(end_frame)],
        )

    def from_beat_cycles(
        self, peak_index: Peaks64, base_ch: int, margin_time: float = 0.25
    ):
        """
        拍動周期ごとのデータに分割してMEAクラスのリストとして返す
        Parameters
        ----------
        peak_index: 読み込みデータ全体のピーク抽出結果
        base_ch: 基準電極
        margin_time: ピークの前後何秒を拍動周期とするか

        Returns list[MEA]
        -------

        """
        result: list[MEA] = []
        half_window = int(margin_time * self.SAMPLING_RATE)
        base_peaks = peak_index[base_ch]
        total_frames = self.array.shape[1]

        for peak in base_peaks:
            start = max(0, peak - half_window)
            end = min(total_frames, peak + half_window)
            result.append(self.from_slice(start, end))

        return result
