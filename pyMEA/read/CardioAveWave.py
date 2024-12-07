import numpy as np

from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.find_peaks.peak_model import NegPeaks
from pyMEA.read.MEA import MEA


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


"""
心筋波形の平均を取ってノイズを除去する
"""


# 1電極の平均波形を算出
def calc_average_wave(data: MEA, neg_peaks: NegPeaks, ele: int, front=500, end=3000):
    waves = np.array([data[ele][p - front : p + end] for p in neg_peaks[ele][1:-1]])
    ave_wave = [waves[:, i].mean() for i in range(len(waves[0]))]
    return np.array(ave_wave)


# 全64電極の平均波形を算出
def calc_64_ave_waves(data: MEA, neg_peaks: NegPeaks, front=0.05, end=0.3):
    front_frame = int(front * data.SAMPLING_RATE)
    end_frame = int(end * data.SAMPLING_RATE)
    ave_waves = np.array(
        [
            [0.0 for _ in range(int(data.SAMPLING_RATE * (front + end)))]
            for _ in range(65)
        ]
    )

    for ch in range(1, 65):
        if len(neg_peaks[ch]) > 3:
            ave_waves[ch] = calc_average_wave(
                data, neg_peaks, ch, front=front_frame, end=end_frame
            )
        else:
            ave_waves[ch] = np.array([0 for _ in range(end_frame + front_frame)])
    ave_waves[0] = np.arange(len(ave_waves[1])) / data.SAMPLING_RATE

    return ave_waves
