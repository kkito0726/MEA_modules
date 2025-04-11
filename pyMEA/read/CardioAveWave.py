import numpy as np
from black.cache import dataclass

from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.find_peaks.peak_model import NegPeaks64
from pyMEA.read.model.MEA import MEA


@dataclass(frozen=True)
class CardioAveWave(MEA):
    front: float = 0.05
    back: float = 0.3
    distance: int = 3000

    def __post_init__(self):
        super().__post_init__()
        neg_peaks = detect_peak_neg(self, self.distance)
        object.__setattr__(
            self, "array", calc_64_ave_waves(self, neg_peaks, self.front, self.back)
        )


"""
心筋波形の平均を取ってノイズを除去する
"""


# 1電極の平均波形を算出
def calc_average_wave(data: MEA, neg_peaks: NegPeaks64, ele: int, front=500, end=3000):
    waves = np.array([data[ele][p - front : p + end] for p in neg_peaks[ele][1:-1]])
    ave_wave = [waves[:, i].mean() for i in range(len(waves[0]))]
    return np.array(ave_wave)


# 全64電極の平均波形を算出
def calc_64_ave_waves(data: MEA, neg_peaks: NegPeaks64, front=0.05, end=0.3):
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
