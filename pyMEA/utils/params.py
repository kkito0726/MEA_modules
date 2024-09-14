import numpy as np
from numpy import ndarray

from pyMEA.find_peaks.peak_detection import detect_peak_pos
from pyMEA.MEA import MEA


# ISIを算出する関数
def calc_isi(peak_index: ndarray, ele: int, sampling_rate=10000):
    return np.diff(peak_index[ele]) / sampling_rate


def calc_fpd(
    data: MEA, neg_peak: np.ndarray, ele: int, peak_range=(30, 110)
) -> list[float]:
    # 1st peak付近のデータを0に変換
    for p in neg_peak[ele]:
        data[ele][p - 200 : p + 200] = 0

    # 各拍動周期で2nd peakを抽出
    fpds = []
    for p in neg_peak[ele]:
        tmp = data[:, p + 200 : p + 5000]  # 2nd peak付近のデータを抽出
        pos_peak = detect_peak_pos(tmp, height=peak_range, distance=3000)
        # ピークが見つからなかったら飛ばして次の拍動周期
        if len(pos_peak[ele]) == 0:
            continue

        pos_time = tmp[0][pos_peak[ele]]
        fpd = pos_time[0] - data[0][p]
        if 0.1 < fpd < 0.4:
            fpds.append(fpd)
        # 範囲外FPDの場合スルー
        else:
            continue

    return fpds


def calc_fpd_params(
    data: MEA, neg_peak: np.ndarray, ele: int, peak_range=(30, 110)
) -> list[float]:
    isi = np.diff(neg_peak[ele]) / data.SAMPLING_RATE
    # 1st peak付近のデータを0に変換
    for p in neg_peak[ele]:
        data[ele][p - 200 : p + 200] = 0

    # 各拍動周期で2nd peakを抽出
    fpds, fpdcBs, fpdcFs = [], [], []
    for index, p in enumerate(neg_peak[ele]):
        tmp = data[:, p + 200 : p + 5000]  # 2nd peak付近のデータを抽出
        pos_peak = detect_peak_pos(tmp, height=peak_range, distance=3000)
        # ピークが見つからなかったら飛ばして次の拍動周期
        if len(pos_peak[ele]) == 0:
            continue

        pos_time = tmp[0][pos_peak[ele]]
        fpd = pos_time[0] - data[0][p]
        if 0.1 < fpd < 0.4:
            fpds.append(fpd)
        # 範囲外FPDの場合スルー
        else:
            continue

        if 0 < index:
            fpdcB = fpd / np.sqrt(isi[index - 1])
            fpdcBs.append(fpdcB)
            fpdcF = fpd / (isi[index - 1] ** (1 / 3))
            fpdcFs.append(fpdcF)

    return fpds, fpdcBs, fpdcFs


# 環状の回路の各電極間の伝導速度
def circuit_velocity(data: ndarray, peak_index: ndarray, eles: list[int]):
    # 電極間分をリストに格納
    cvs = [0 for i in range(len(eles))]

    for i in range(len(eles) - 1):
        # ピークの数が0でないかつ隣の電極とピーク数が同じである場合は伝導速度を算出
        if len(peak_index[eles[i]]) != 0 and len(peak_index[eles[i]]) == len(
            peak_index[eles[i + 1]]
        ):
            time = abs(data[0][peak_index[eles[i + 1]]] - data[0][peak_index[eles[i]]])
            cv = 450 * 10**-6 / time
            cvs[i] = cv
    # 最初と最後の電極間の伝導速度を算出
    if len(peak_index[eles[-1]]) != 0 and len(peak_index[eles[-1]]) == len(
        peak_index[eles[0]]
    ):
        time = abs(data[0][peak_index[eles[-1]]] - data[0][peak_index[eles[0]]])
        cv = 450 * 10**-6 / time
        cvs[-1] = cv

    return cvs
