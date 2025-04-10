from dataclasses import dataclass
from typing import Sequence

from numpy import array_equal, ndarray
from numpy._typing import NDArray

from pyMEA.utils.decorators import ch_validator


# 1つの電極で取得したピーク
@dataclass(frozen=True)
class Peaks:
    peak_index: ndarray

    def __getitem__(self, ch: int):
        return self.peak_index[ch]

    def __repr__(self):
        return repr(self.peak_index)

    def __len__(self):
        return len(self.peak_index)

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
class Peaks64:
    def __init__(self, peak_index: Sequence[Peaks]):
        if len(peak_index) != 65:
            raise ValueError(f"peak_indexの要素数エラー 要素数: {len(peak_index)}")
        self.peaks = {ch: peak_index[ch] for ch in range(1, 65)}

    @ch_validator
    def __getitem__(self, ch) -> Peaks:
        return self.peaks[ch]

    def __repr__(self):
        return repr(self.peaks)

    def __len__(self) -> int:
        return len(self.peaks)


class NegPeaks64(Peaks64):
    def __init__(self, peak_index: NDArray[NegPeaks]):
        super().__init__(peak_index)

    @ch_validator
    def __getitem__(self, ch) -> NegPeaks:
        return super().__getitem__(ch)


class PosPeaks64(Peaks64):
    def __init__(self, peak_index: NDArray[PosPeaks]):
        super().__init__(peak_index)

    @ch_validator
    def __getitem__(self, ch) -> PosPeaks:
        return super().__getitem__(ch)


class AllPeaks64(Peaks64):
    def __init__(self, peak_index: NDArray[Peaks]):
        super().__init__(peak_index)
