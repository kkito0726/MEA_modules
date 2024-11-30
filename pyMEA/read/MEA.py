from numpy import ndarray

from pyMEA.read.model.HedPath import HedPath
from pyMEA.read.read_bio import decode_hed, hed2array
from pyMEA.utils.decorators import time_validator


class MEA:
    @time_validator
    def __init__(self, hed_path: str, start: int = 0, end: int = 120) -> None:
        """
        Args:
            hed_path: .hedファイルのパス
            start: 読み込み開始時間 [s]
            end: 読み込み終了時間[s]
        """
        self._hed_path: HedPath = HedPath(hed_path)
        self._start: int = start
        self._end: int = end
        self._time: int = end - start
        self._SAMPLING_RATE, self._GAIN = decode_hed(self._hed_path)
        self._array = hed2array(self._hed_path, self._start, self._end)

    def __repr__(self):
        return repr(self.array)

    def __getitem__(self, index: int) -> ndarray:
        return self.array[index]

    def __len__(self) -> int:
        return len(self.array)

    def __add__(self, value):
        return self.array + value

    def __sub__(self, value):
        return self._array - value

    def __mul__(self, value):
        return self._array * value

    def __truediv__(self, value):
        return self._array / value

    def __floordiv__(self, value):
        return self._array // value

    @property
    def info(self) -> str:
        info = f"読み込み開始時間  : {self.start} s\n読み込み終了時間  : {self.end} s\n読み込み合計時間  : {self.time} s\nサンプリングレート: {self.SAMPLING_RATE} Hz\nGAIN           : {self.GAIN}"
        print(info)
        return info

    @property
    def shape(self) -> tuple[int, ...]:
        return self.array.shape

    @property
    def hed_path(self) -> str:
        return self._hed_path

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end

    @property
    def time(self) -> int:
        return self._time

    @property
    def SAMPLING_RATE(self) -> int:
        return self._SAMPLING_RATE

    @property
    def GAIN(self) -> int:
        return self._GAIN

    @property
    def array(self):
        return self._array
