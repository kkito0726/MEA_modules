"""ピーク時刻行列の生成と、ピーク未検出電極の除去。

各電極のピーク検出数の最頻値と異なる電極 (ピークを正しく検出できていない電極)
を除外し、拍動周期ごとのピーク時刻行列を返す。
"""

import statistics

import numpy as np

from pyMEA.constants import NUM_ELECTRODES
from pyMEA.domain.model.MEA import MEA
from pyMEA.domain.model.peak_model import Peaks64


def remove_undetected_ch(
    data: MEA, peak_index: Peaks64, chs: list[int]
) -> tuple[np.ndarray, list[int]]:
    """
    指定電極のうちピーク未検出の電極を除去したピーク時刻行列を返す

    Returns:
        times: 拍動周期ごとのピーク時刻行列 (s)
        remove_ch_index: 除去した電極のchsにおけるインデックス
    """
    # ピークの時刻 (s)を取得
    time = [data[0][peak_index[ch]] for ch in chs]

    # 各電極の取得ピーク数の最頻値以外の電極は削除
    peaks = [len(peak_index[ch]) for ch in chs]
    mode_peaks = statistics.mode(peaks)
    remove_ch_index = [i for i in range(len(time)) if len(time[i]) != mode_peaks]

    # ピークを正しく検出できていないchのデータを削除
    for ch in sorted(remove_ch_index, reverse=True):
        time.pop(ch)
    print("弾いた電極番号: ", np.array(remove_ch_index))

    times = np.array(
        [[time[i][j] for i in range(len(time))] for j in range(len(time[0]))]
    )

    return times, remove_ch_index


def remove_undetected_ch_from64ch(
    data: MEA, peak_index: Peaks64
) -> tuple[np.ndarray, list[int]]:
    """
    全64電極のうちピーク未検出の電極を除去したピーク時刻行列を返す
    """
    return remove_undetected_ch(data, peak_index, list(range(1, NUM_ELECTRODES + 1)))
