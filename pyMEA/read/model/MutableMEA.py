from numpy import ndarray

from pyMEA.read.model.HedPath import HedPath
from pyMEA.read.read_bio import decode_hed, hed2array
from pyMEA.utils.decorators import time_validator


class MutableMEA:
    @time_validator
    def __init__(self, hed_path: str, start: int = 0, end: int = 120) -> None:
        """
        Args:
            hed_path: .hedファイルのパス
            start: 読み込み開始時間 [s]
            end: 読み込み終了時間[s]
        """
        self.hed_path: HedPath = HedPath(hed_path)
        self.start: int = start
        self.end: int = end
        self.time: int = end - start
        self.SAMPLING_RATE, self.GAIN = decode_hed(self.hed_path)
        self.array = hed2array(self.hed_path, self.start, self.end)

    def __repr__(self):
        return repr(self.array)

    def __getitem__(self, index: int) -> ndarray:
        return self.array[index]

    def __len__(self) -> int:
        return len(self.array)

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
