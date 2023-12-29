from peak_detection import detect_peak_neg
import numpy as np
from numpy import ndarray
from scipy.signal import savgol_filter, find_peaks


# ISIを算出する関数
def calc_isi(MEA_data: ndarray, ele: int):
    # 1st peakを抽出
    peak_index = detect_peak_neg(MEA_data)
    peak_time = MEA_data[0][peak_index[ele]]
    isi = np.diff(peak_time)

    return isi


def calc_fpd(
    MEA_data: ndarray, ele: ndarray, window=30, height=(10, 80), sampling_rate=10000
):
    # 任意の電極の1st peakを抽出
    peak_neg = detect_peak_neg(MEA_data)[ele]
    data = np.copy(MEA_data[ele])

    # 先頭の1st peakより前のデータは0に置き換える
    data[: peak_neg[0]] = 0

    # 1st peakの前のデータを0に置き換えて不要なピークを潰す
    for idx in peak_neg:
        data[idx - 500 : idx] = 0

    # データをスムージングしてピーク抽出する
    smooth = savgol_filter(data, window, 0)
    peaks, _ = find_peaks(smooth, height=height)

    fpd = (peaks - peak_neg[: len(peaks)]) / sampling_rate

    return fpd


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
