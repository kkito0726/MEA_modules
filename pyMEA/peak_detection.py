import numpy as np
from numpy import ndarray
from scipy.signal import find_peaks


# 64電極すべての下ピークを取得
def detect_peak_neg(
    MEA_data: ndarray,
    distance=5000,
    threshold=3,
    min_amp=10,
    width=None,
    prominence=None,
) -> ndarray:
    peak_index = np.array([None for _ in range(len(MEA_data))])
    for i in range(1, len(MEA_data)):
        # ピーク抽出の閾値を設定
        height = np.std(MEA_data[i]) * threshold
        # 閾値が最低閾値を下回っていた場合は最低閾値の値を閾値の値に設定する
        if height < min_amp:
            height = min_amp
        detect_peak_index = find_peaks(
            -MEA_data[i],
            height=height,
            distance=distance,
            width=width,
            prominence=prominence,
        )

        peak_index[i] = detect_peak_index[0]
        peak_index[i] = np.sort(peak_index[i])
    peak_index[0] = np.array([])

    return peak_index


# 64電極すべての上ピークを取得
def detect_peak_pos(
    MEA_data: ndarray,
    distance=10000,
    width=None,
    prominence=None,
    height: tuple[int] = (10, 80),
) -> ndarray:
    peak_index = np.array([None for _ in range(len(MEA_data))])
    for i in range(1, len(MEA_data)):
        # height = np.std(MEA_data[i]) * 3
        detect_peak_index = find_peaks(
            MEA_data[i],
            height=height,
            distance=distance,
            width=width,
            prominence=prominence,
        )

        peak_index[i] = detect_peak_index[0]
        peak_index[i] = np.sort(peak_index[i])
    peak_index[0] = np.array([])

    return peak_index


# 64電極すべての上下ピークを取得
def detect_peak_all(
    MEA_data: ndarray,
    threshold: list[int] = [3, 3],
    distance=3000,
    width=None,
    prominence=None,
) -> ndarray:
    peak_index = np.array([None for _ in range(len(MEA_data))])
    for i in range(1, 65):
        # +のデータだけでSDを計算してthresholdを決定する
        pos_data = MEA_data[i].copy()
        pos_data[pos_data < 0] = 0
        pos_height = np.std(pos_data) * threshold[0]
        # ピーク抽出
        peak_pos, _ = find_peaks(
            MEA_data[i],
            height=pos_height,
            distance=distance,
            width=width,
            prominence=prominence,
        )

        # -のデータだけでSDを計算してthresholdを決定する
        neg_data = MEA_data[i].copy()
        neg_data[neg_data > 0] = 0
        neg_height = np.std(neg_data) * threshold[1]
        # ピーク抽出
        peak_neg, _ = find_peaks(
            -MEA_data[i],
            height=neg_height,
            distance=distance,
            width=width,
            prominence=prominence,
        )

        peak_index[i] = np.append(peak_pos, peak_neg)
        peak_index[i] = np.sort(peak_index[i])

    peak_index[0] = np.array([])

    return peak_index
