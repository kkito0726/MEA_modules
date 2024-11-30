import numpy as np
from numpy import ndarray

from pyMEA.find_peaks.peak_model import NegPeaks
from pyMEA.read.MEA import MEA


def filter_fft(MEA_data: ndarray, fc=200, sampling_rate=10000) -> ndarray:
    """
    フーリエ解析を用いで波形のノイズ除去を行う。\n
    Parameters
    ----------
      MEA_data: hed2array()で読み込んだ計測データ\n
      fc: カットオフ周波数\n
      sampling_rate: サンプリングレート\n
    """
    # 配列の初期化
    filter_data = np.array([None for _ in range(len(MEA_data))])
    filter_data[0] = MEA_data[0]

    # 周波数軸のデータ
    fq = np.linspace(0, sampling_rate, len(MEA_data[0]))
    # カットオフ周波数の上限を設定
    fc_upper = sampling_rate - fc

    for i in range(1, len(MEA_data)):
        f = np.fft.fft(MEA_data[i])
        f[((fq > fc) & (fq < fc_upper))] = 0

        # 逆フーリエ変換して、複素数の実部のみを採用
        filter_data[i] = np.fft.ifft(f).real

    return filter_data


"""
移動平均によってノイズ除去
"""


def get_moving_average(
    data: MEA, ch, start_flame, wave_length=200, steps=10
) -> ndarray:
    mean_50hz = np.zeros(wave_length)

    # steps回数分の波形データを加算する
    for s in range(steps):
        mean_50hz += data[ch][start_flame + (200 * s) : start_flame + (200 * (s + 1))]

    return mean_50hz / steps


def filter_by_moving_average(data: MEA, power_noise_freq=50, steps=10) -> ndarray:
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
