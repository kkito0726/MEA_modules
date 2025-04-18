from typing import List

import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray

from pyMEA.read.model.MEA import MEA

circuit_eles = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    16,
    24,
    32,
    40,
    48,
    56,
    64,
    63,
    62,
    61,
    60,
    59,
    58,
    57,
    49,
    41,
    33,
    25,
    17,
    9,
]


# 64電極すべての電極の波形を出力
def showAll(
    MEA_data: ndarray,
    sampling_rate=10000,
    start=0,
    end=5,
    volt_min=-200,
    volt_max=200,
    figsize=(8, 8),
    dpi=300,
) -> None:
    start_frame = int(start * sampling_rate)
    end_frame = int(end * sampling_rate)

    plt.figure(figsize=figsize, dpi=dpi)
    for i in range(1, 65, 1):
        plt.subplot(8, 8, i)
        plt.plot(MEA_data[0][start_frame:end_frame], MEA_data[i][start_frame:end_frame])
        # plt.xlim(start, end)
        plt.ylim(volt_min, volt_max)

    plt.show()


# 外周のデータを表示
def circuit(
    MEA_raw: ndarray,
    start=0,
    end=5,
    sampling_rate=10000,
    xlabel="Time (s)",
    ylabel="Electrode Number",
    figsize=(8, 8),
    dpi=300,
) -> None:
    MEA_data = []
    for ele in circuit_eles:
        MEA_data.append(MEA_raw[ele])

    data = np.array(MEA_data)
    start_frame = int(start * sampling_rate)
    end_frame = int(end * sampling_rate)

    plt.figure(figsize=figsize, dpi=dpi)
    for i, index in enumerate(np.array(data)):
        tmp_volt = (index - np.mean(index)) / 200
        plt.plot(MEA_raw[0][start_frame:end_frame], tmp_volt[start_frame:end_frame] + i)

    plt.xlim(start, end)
    plt.yticks(range(0, len(circuit_eles), 1))
    plt.ylim(-1, len(circuit_eles))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


# 任意の電極データを一つのグラフに表示
def showDetection(
    MEA_raw: MEA,
    eles: List[int],
    start=0,
    end=5,
    read_start=None,  # データの読み込み開始時間 (s)読み込み時間によるframeのずれを解消する
    sampling_rate=10000,
    adjust_wave=200,
    figsize=(12, 12),
    xlabel="Time (s)",
    ylabel="Electrode Number",
    dpi=300,
) -> None:
    MEA_data = []
    for ele in eles:
        MEA_data.append(MEA_raw[ele])

    data = np.array(MEA_data)
    start_frame = int(start * sampling_rate)
    end_frame = int(end * sampling_rate)

    plt.figure(figsize=figsize, dpi=dpi)
    for i, index in enumerate(np.array(data)):
        tmp_volt = (index - np.mean(index)) / adjust_wave
        plt.plot(MEA_raw[0][start_frame:end_frame], tmp_volt[start_frame:end_frame] + i)

    ele_label = [str(eles[i]) for i in range(len(eles))]
    plt.yticks(range(0, len(eles), 1), ele_label)

    # 読み込み開始時間が途中からの場合のズレを解消する
    if read_start:
        plt.xlim(start + read_start, end + read_start)
    else:
        plt.xlim(start, end)
    plt.ylim(-1, len(eles))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.show()
