from dataclasses import dataclass

from numpy import array_equal, int64
from numpy._typing import NDArray

from pyMEA.utils.decorators import ch_validator


# 1つの電極で取得したピーク
@dataclass(frozen=True)
class Peaks:
    peak_index: NDArray[int64]

    def __getitem__(self, ch: int):
        return self.peak_index[ch]

    def __repr__(self):
        return repr(self.peak_index)

    def __len__(self):
        return len(self.peak_index)

    def __iter__(self):
        return iter(self.peak_index)

    def __add__(self, value):
        return self.peak_index + value

    def __sub__(self, value):
        return self.peak_index - value

    def __mul__(self, value):
        return self.peak_index * value

    def __truediv__(self, value):
        return self.peak_index / value

    def __floordiv__(self, value):
        return self.peak_index // value

    def __eq__(self, other):
        if isinstance(other, Peaks):
            return array_equal(self.peak_index, other.peak_index)
        return False

    def __ne__(self, other):
        return self.peak_index != other

    def __lt__(self, other):
        return self.peak_index < other

    def __le__(self, other):
        return self.peak_index <= other

    def __gt__(self, other):
        return self.peak_index > other

    def __ge__(self, other):
        return self.peak_index >= other


# 1つの電極のマイナス方向のピーク
class NegPeaks(Peaks):
    pass


# 1つの電極のプラス方向のピーク
class PosPeaks(Peaks):
    pass


# 64電極分のピークをまとめたオブジェクト
@dataclass(frozen=True)
class Peaks64:
    peaks: dict[int, Peaks]

    @ch_validator
    def __getitem__(self, ch) -> Peaks:
        return self.peaks[ch]

    def __repr__(self):
        return repr(self.peaks)

    def __len__(self) -> int:
        return len(self.peaks)

    def __iter__(self):
        return iter(self.peaks)


@dataclass(frozen=True)
class NegPeaks64(Peaks64):
    @ch_validator
    def __getitem__(self, ch) -> Peaks:
        return super().__getitem__(ch)


@dataclass(frozen=True)
class PosPeaks64(Peaks64):
    @ch_validator
    def __getitem__(self, ch) -> Peaks:
        return super().__getitem__(ch)


@dataclass(frozen=True)
class AllPeaks64(Peaks64):
    @ch_validator
    def __getitem__(self, ch) -> Peaks:
        return super().__getitem__(ch)
