from numpy import ndarray

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
        self.__hed_path: str = hed_path
        self.__start: int = start
        self.__end: int = end
        self.__time: int = end - start
        self.__SAMPLING_RATE, self.__GAIN = decode_hed(self.__hed_path)
        self._array = hed2array(self.__hed_path, self.__start, self.__end)

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
        return self.__hed_path

    @property
    def start(self) -> int:
        return self.__start

    @property
    def end(self) -> int:
        return self.__end

    @property
    def time(self) -> int:
        return self.__time

    @property
    def SAMPLING_RATE(self) -> int:
        return self.__SAMPLING_RATE

    @property
    def GAIN(self) -> int:
        return self.__GAIN

    @property
    def array(self):
        return self._array
