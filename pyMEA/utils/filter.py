import numpy as np
from numpy import ndarray


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
