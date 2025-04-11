import numpy as np

from pyMEA.read.model.MEA import MEA


class FilterMEA(MEA):
    power_noise_freq: int = 50
    steps: int = 10

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(
            self,
            "array",
            filter_by_moving_average(self, self.power_noise_freq, self.steps),
        )


"""
移動平均によってノイズ除去
"""


def get_moving_average(
    data: MEA, ch, start_flame, wave_length=200, steps=10
) -> np.ndarray:
    mean_50hz = np.zeros(wave_length)

    # steps回数分の波形データを加算する
    for s in range(steps):
        mean_50hz += data[ch][start_flame + (200 * s) : start_flame + (200 * (s + 1))]

    return mean_50hz / steps


def filter_by_moving_average(data: MEA, power_noise_freq=50, steps=10) -> np.ndarray:
    data_length = len(data[0])
    wave_length = int(data.SAMPLING_RATE / power_noise_freq)
    num_wave = int(data_length / wave_length)

    # 各フレームの開始位置を取得
    time_frames = np.array([i * wave_length for i in range(num_wave)])

    # 移動平均の計算上最後のステップ回数分のフレームは飛び出さないように同じ数を繰り返す。
    start_frames = np.array([i * wave_length for i in range(num_wave)])
    start_frames[-steps:] = start_frames[-steps - 1]

    # ノイズデータの初期化
    elc_noise = np.zeros((64 + 1, data_length))

    for ch in range(1, 65):
        # 各周期の移動平均を算出
        for start_frame, time_frame in zip(start_frames, time_frames):
            elc_noise[ch][time_frame : time_frame + wave_length] = get_moving_average(
                data, ch, start_frame
            )

    return data - elc_noise
