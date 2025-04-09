import statistics
from typing import Any, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray
from scipy.optimize import curve_fit

from pyMEA.find_peaks.peak_model import Peaks64
from pyMEA.read.MEA import MEA


def remove_undetected_ch(
    data: MEA, peak_index: Peaks64
) -> tuple[list[list[ndarray[Any, Any]]], list[int]]:
    # ピークの時刻 (s)を取得
    time = [data[0][peak_index[i]] for i in range(1, 65)]

    # 各電極の取得ピーク数の最頻値以外の電極は削除
    peaks = [len(peak_index[i]) for i in range(1, 65)]
    remove_ch = []
    for i in range(len(time)):
        if len(time[i]) != statistics.mode(peaks):
            remove_ch.append(i)

    # ピークを正しく検出できていないchのデータを削除
    for ch in sorted(remove_ch, reverse=True):
        time.pop(ch)
    print("弾いた電極番号: ", np.array(remove_ch))

    res = []
    for j in range(len(time[0])):
        res.append([time[i][j] for i in range(len(time))])

    return res, remove_ch


def get_mesh(ele_dis: int, mesh_num: int):
    # データ範囲を取得
    x_min, x_max = 0, ele_dis * 7
    y_min, y_max = 0, ele_dis * 7

    # 取得したデータ範囲で新しく座標にする配列を作成
    x_coord = np.linspace(x_min, x_max, mesh_num)
    y_coord = np.linspace(y_min, y_max, mesh_num)

    # 取得したデータ範囲で新しく座標にする配列を作成
    xx, yy = np.meshgrid(x_coord, y_coord)

    # 電極番号順に配列を修正
    yy = np.rot90(np.rot90(yy))

    return xx, yy


# この三次関数(2変数)に測定値をフィッティングする。


def model(X, p00, p10, p01, p20, p11, p02, p30, p21, p12, p03):
    x, y = X
    z = (
        p00
        + p10 * x
        + p01 * y
        + p20 * x**2
        + p11 * x * y
        + p02 * y**2
        + p30 * x**3
        + p21 * x**2 * y
        + p12 * x * y**2
        + p03 * y**3
    )
    return z.ravel()


# フィッティング関数


def fit_data(
    times: ndarray, remove_ch: List[int], ele_dis: int
) -> tuple[ndarray, ndarray]:
    xx, yy = get_mesh(ele_dis, 8)
    xx = np.delete(xx, remove_ch)
    yy = np.delete(yy, remove_ch)

    popts, r2s = [], []
    for time in times:
        popt, pcov = curve_fit(model, [xx, yy], time)
        popts.append(popt)

        residuals = time - model([xx, yy], *popt)
        rss = np.sum(residuals**2)
        tss = np.sum((time - np.mean(time)) ** 2)
        r2 = 1 - (rss / tss)
        r2s.append(r2)

    return np.array(popts), np.array(r2s)


def remove_fit_data(
    data: MEA, peak_index: Peaks64, ele_dis: int
) -> tuple[ndarray, ndarray]:
    # ピーク抽出できなかった電極のデータは除去する
    times, remove_ch = remove_undetected_ch(data, peak_index)
    return fit_data(times, remove_ch, ele_dis)


# 2dカラーマップを描画


def draw_2d(
    popts: ndarray,
    ele_dis: int,
    mesh_num: int,
    contour=False,
    isQuiver=False,
    xlabel="X (μm)",
    ylabel="Y (μm)",
    clabel="Δt (ms)",
    dpi=300,
    cmap="jet",
) -> None:
    # grid配列を生成
    xx, yy = get_mesh(ele_dis, mesh_num)
    ex, ey = get_mesh(ele_dis, 8)

    for popt in popts:
        # フィッティングした関数からデータを生成
        z = model([xx, yy], *popt)
        z -= np.min(z)
        z *= 1000

        # 電極上の勾配を算出する
        z_ele = model([ex, ey], *popt)
        grady, gradx = np.gradient(z_ele.reshape(8, 8), ele_dis * 7 / (8 - 1) * 10**-6)
        cx, cy = gradx / (gradx**2 + grady**2), grady / (gradx**2 + grady**2)

        # グラフにプロットする
        fig = plt.figure(dpi=dpi)
        ax = fig.add_subplot(111)
        ax.set_aspect("equal", adjustable="box")
        if contour:
            c = ax.contourf(xx, yy, z.reshape(mesh_num, mesh_num), cmap=cmap)
            ax.contour(
                xx,
                yy,
                z.reshape(100, 100),
                colors="k",
                linewidths=0.5,
                linestyles="solid",
            )
        else:
            c = ax.pcolormesh(xx, yy, z.reshape(mesh_num, mesh_num), cmap=cmap)
        plt.scatter(ex, ey, marker=",", color="grey")
        if isQuiver:
            plt.quiver(ex, ey, cx, -cy)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        bar = plt.colorbar(c)
        bar.set_label(clabel)
        plt.xticks(np.arange(0, ele_dis * 7 + 1, ele_dis))
        plt.yticks(np.arange(0, ele_dis * 7 + 1, ele_dis))

        plt.show()


# 3dカラーマップを描画


def draw_3d(
    popts: ndarray,
    ele_dis: int,
    mesh_num: int,
    xlabel="",
    ylabel="",
    clabel="",
    dpi=300,
) -> None:
    xx, yy = get_mesh(ele_dis, mesh_num)

    for popt in popts:
        # フィッティングした関数からデータを生成
        z = model([xx, yy], *popt)
        z -= np.min(z)
        z *= 1000

        # グラフにプロットする
        fig = plt.figure(dpi=dpi)
        ax = fig.add_subplot(111, projection="3d")
        c = ax.plot_surface(xx, yy, z.reshape(mesh_num, mesh_num), cmap="jet")
        bar = fig.colorbar(c)
        bar.set_label(clabel)
        plt.xticks(np.arange(0, ele_dis * 7 + 1, ele_dis))
        plt.yticks(np.arange(0, ele_dis * 7 + 1, ele_dis))
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        fig.show()


# 伝導速度の算出


def calc_gradient_velocity(popts: ndarray, ele_dis: int, mesh_num=8) -> ndarray:
    xx, yy = get_mesh(ele_dis, mesh_num)

    cvs_list = []
    for popt in popts:
        z = model([xx, yy], *popt)
        grady, gradx = np.gradient(
            z.reshape(mesh_num, mesh_num), np.diff(xx)[0][0] * 10**-6
        )
        cx, cy = gradx / (gradx**2 + grady**2), grady / (gradx**2 + grady**2)
        cvs = np.sqrt(cx**2 + cy**2).ravel()
        cvs_list.append(cvs)

    return np.array(cvs_list)
