from dataclasses import dataclass, field
from typing import Any

from numpy import dtype, ndarray

from pyMEA.read.model.HedPath import HedPath
from pyMEA.read.read_bio import decode_hed, hed2array


@dataclass(frozen=True)
class MEA:
    hed_path: str
    start: int
    end: int
    SAMPLING_RATE: int = field(init=False)
    GAIN: int = field(init=False)
    array: ndarray[Any, dtype] = field(init=False)

    def __post_init__(self):
        hed_path = HedPath(self.hed_path)
        SAMPLING_RATE, GAIN = decode_hed(hed_path)
        array = hed2array(hed_path, self.start, self.end)
        object.__setattr__(self, "SAMPLING_RATE", SAMPLING_RATE)
        object.__setattr__(self, "GAIN", GAIN)

        # object.__setattr__ を使って frozen dataclass の内部を書き換える
        object.__setattr__(self, "array", self._freeze_array(array))

    @staticmethod
    def _freeze_array(arr: ndarray[Any]) -> ndarray[Any]:
        arr.setflags(write=False)
        return arr

    @property
    def time(self):
        return self.end - self.start

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
