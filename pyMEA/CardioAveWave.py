from pyMEA.MEA import MEA
from pyMEA.filter import calc_64_ave_waves
from pyMEA.peak_detection import detect_peak_neg


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
        self.array = calc_64_ave_waves(self, neg_peaks, front, back)

        self.start = 0
        self.end = back
