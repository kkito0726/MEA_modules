from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.read.MEA import MEA
from pyMEA.utils.filter import calc_64_ave_waves


class CardioAveWave(MEA):
    def __init__(
        self,
        hed_path: str,
        start: int = 0,
        end: int = 120,
        front=0.05,
        back=0.3,
        distance=3000,
    ) -> None:
        super().__init__(hed_path, start, end)
        neg_peaks = detect_peak_neg(self, distance)
        self._array = calc_64_ave_waves(self, neg_peaks, front, back)

        self._start = 0
        self._end = front + back
        self._time = self.end - self.start
