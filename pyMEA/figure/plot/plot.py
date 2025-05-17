import statistics
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray
from scipy.interpolate import interp1d
from matplotlib.collections import LineCollection

from pyMEA.core.Electrode import Electrode
from pyMEA.find_peaks.peak_model import Peaks64
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


def draw_line_conduction(data: MEA, ele_dis, peak_index: Peaks64, chs: list[int]):
    times, chs = remove_undetected_ch(data, peak_index, chs)
    # 各拍動周期について処理していく
    for time in times:
        t = time - time.min()
        t = t * 10**3  # 単位をmsに変換

        electrode = Electrode(ele_dis)
        x = np.array([electrode.get_coordinate(ch)[0] for ch in chs])
        y = np.array([electrode.get_coordinate(ch)[1] for ch in chs])

        # === 通過順ベースの補間 ===
        s = np.linspace(0, 1, len(x))  # parametric distance
        num_interp = 300
        s_fine = np.linspace(0, 1, num_interp)

        fx = interp1d(s, x, kind="linear")
        fy = interp1d(s, y, kind="linear")
        ft = interp1d(s, t, kind="linear")  # 色付け用の補間

        x_fine = fx(s_fine)
        y_fine = fy(s_fine)
        t_fine = ft(s_fine)

        # === 線分生成 ===
        points = np.array([x_fine, y_fine]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # === グラデーション表示 ===
        norm = plt.Normalize(t.min(), t.max())
        lc = LineCollection(segments, cmap="jet", norm=norm, zorder=5)
        lc.set_array(t_fine[:-1])
        lc.set_linewidth(3)

        # === 描画 ===
        fig, ax = plt.subplots()
        line = ax.add_collection(lc)
        fig.colorbar(line, ax=ax, label="Δt (ms)")

        # === メッシュ表示 ===
        mx, my = electrode.get_mesh
        plt.scatter(mx, my, marker=",", color="grey", zorder=10)

        ele_range = electrode.ele_dis * 7
        margin_ratio = 0.05

        ax.set_xlim(0 - ele_range * margin_ratio, ele_range + ele_range * margin_ratio)
        ax.set_ylim(0 - ele_range * margin_ratio, ele_range + ele_range * margin_ratio)

        ax.set_aspect("equal")
        plt.xlabel("X (μm)")
        plt.ylabel("Y (μm)")
        plt.xticks(np.arange(0, electrode.ele_dis * 7 + 1, electrode.ele_dis))
        plt.yticks(np.arange(0, electrode.ele_dis * 7 + 1, electrode.ele_dis))
        plt.show()


def remove_undetected_ch(data: MEA, peak_index: Peaks64, chs: list[int]):
    # ピークの時刻 (s)を取得
    time = [data[0][peak_index[ch]] for ch in chs]

    # 各電極の取得ピーク数の最頻値以外の電極は削除
    peaks = [len(peak_index[ch]) for ch in chs]
    remove_ch_index = []
    for i in range(len(time)):
        if len(time[i]) != statistics.mode(peaks):
            remove_ch_index.append(i)

    # ピークを正しく検出できていないchのデータを削除
    for ch in sorted(remove_ch_index, reverse=True):
        time.pop(ch)
        chs.pop(ch)
    print("弾いた電極番号: ", np.array(remove_ch_index))

    times = []
    for j in range(len(time[0])):
        times.append([time[i][j] for i in range(len(time))])

    return np.array(times), chs
