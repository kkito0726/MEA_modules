import numpy as np
from numpy import ndarray
from scipy.signal import find_peaks

from pyMEA.find_peaks.peak_model import (
    AllPeaks64,
    NegPeaks,
    NegPeaks64,
    Peaks,
    PosPeaks,
    PosPeaks64,
)
from pyMEA.read.model.MEA import MEA


# 64電極すべての下ピークを取得
def detect_peak_neg(
    MEA_data: MEA,
    distance=3000,
    threshold=3,
    min_amp=10,
    width=None,
    prominence=None,
) -> NegPeaks64:
    """
    64電極すべての下ピークを取得

    Args:
        MEA_data: MEA読み込みデータ
        distance: ピークを取る間隔
        threshold: SD * thresholdより大きいピークを取る
        min_amp: 最小のピークの閾値
        width:
        prominence:
    """
    peak_dict: dict[int, NegPeaks] = {}
    for i in range(1, len(MEA_data)):
        # ピーク抽出の閾値を設定
        height = np.std(MEA_data[i]) * threshold
        # 閾値が最低閾値を下回っていた場合は最低閾値の値を閾値の値に設定する
        if height < min_amp:
            height = min_amp

        data = MEA_data.array[i].copy()
        data[data > 0] = 0
        detect_peak_index, _ = find_peaks(
            -data,
            height=height,
            distance=distance,
            width=width,
            prominence=prominence,
        )
        peak_dict[i] = NegPeaks(detect_peak_index)

    return NegPeaks64(peak_dict)


# 64電極すべての上ピークを取得
def detect_peak_pos(
    MEA_data: MEA,
    distance=3000,
    threshold=3,
    min_amp=10,
    width=None,
    prominence=None,
) -> PosPeaks64:
    """
    64電極すべての上ピークを取得

    Args:
        MEA_data: MEA読み込みデータ
        distance: ピークを取る間隔
        threshold: SD * thresholdより大きいピークを取る
        min_amp: 最小のピークの閾値
        width:
        prominence:
    """
    peak_dict: dict[int, PosPeaks] = {}
    for i in range(1, len(MEA_data)):
        # ピーク抽出の閾値を設定
        height = np.std(MEA_data[i]) * threshold
        # 閾値が最低閾値を下回っていた場合は最低閾値の値を閾値の値に設定する
        if height < min_amp:
            height = min_amp

        data = MEA_data.array[i].copy()
        data[data < 0] = 0
        detect_peak_index, _ = find_peaks(
            data,
            height=height,
            distance=distance,
            width=width,
            prominence=prominence,
        )
        peak_dict[i] = PosPeaks(detect_peak_index)

    return PosPeaks64(peak_dict)


def detect_cardio_second_peak(
    MEA_data: MEA,
    distance=3000,
    width=None,
    prominence=None,
    height: tuple[int, int] = (10, 200),
) -> PosPeaks64:
    peak_dict: dict[int, PosPeaks] = {}
    for i in range(1, len(MEA_data)):
        detect_peak_index, _ = find_peaks(
            MEA_data[i],
            height=height,
            distance=distance,
            width=width,
            prominence=prominence,
        )
        peak_dict[i] = PosPeaks(detect_peak_index)

    return PosPeaks64(peak_dict)


# 64電極すべての上下ピークを取得
def detect_peak_all(
    MEA_data: MEA,
    threshold: tuple[int, int] = (3, 3),
    distance=3000,
    min_amp=(10, 10),
    width=None,
    prominence=None,
) -> AllPeaks64:
    """
    64電極すべての上下ピークを取得

    Args:
        MEA_data: MEA読み込みデータ
        threshold: (上threshold, 下threshold)
        distance: ピークを取る間隔
        min_amp: (上の最小閾値電位, 下の最小閾値電位)
        width
        prominence
    """
    peak_pos = detect_peak_pos(
        MEA_data, distance, threshold[0], min_amp[0], width, prominence
    )
    peak_neg = detect_peak_neg(
        MEA_data, distance, threshold[1], min_amp[1], width, prominence
    )
    peak_dict: dict[int, Peaks] = {}
    for i in range(1, 65):
        array = np.array([*peak_pos[i], *peak_neg[i]]).astype(np.int64)
        peak_dict[i] = Peaks(np.sort(array))

    return AllPeaks64(peak_dict)


# レーザー照射によるアーティファクトを除去
def remove_artifact(
    MEA_data: ndarray, artifact_peaks: ndarray, front_frame=8500, end_frame=20000
) -> tuple[ndarray, ndarray]:
    remove_times = []
    for i in range(1, 65):
        for peak in artifact_peaks:
            start_frame = peak - front_frame
            finish_frame = peak + end_frame
            MEA_data[i][start_frame:finish_frame] = 0

            # アーティファクト除去時間は全電極で共通であるため、1回だけ記録する
            if i == 1:
                remove_times.append(
                    [MEA_data[0][start_frame], MEA_data[0][finish_frame]]
                )

    return MEA_data, np.array(remove_times)
