from numpy import ndarray

from pyMEA.utils.decorators import ch_validator


class Peaks:
    def __init__(self, peak_index: ndarray):
        if len(peak_index) != 65:
            raise ValueError(f"peak_indexの要素数エラー 要素数: {len(peak_index)}")

        peaks: dict[int, ndarray] = {}
        for ch in range(1, 65):
            peaks[ch] = peak_index[ch]

        self.peaks = peaks

    @ch_validator
    def __getitem__(self, ch) -> ndarray:
        return self.peaks[ch]

    def __repr__(self):
        return repr(self.peaks)

    def __len__(self) -> int:
        return len(self.peaks)


class NegPeaks(Peaks):
    def __init__(self, peak_index: ndarray):
        super().__init__(peak_index)


class PosPeaks(Peaks):
    def __init__(self, peak_index: ndarray):
        super().__init__(peak_index)


class AllPeaks(Peaks):
    def __init__(self, peak_index: ndarray):
        super().__init__(peak_index)
