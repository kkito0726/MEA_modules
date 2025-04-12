import statistics
from typing import Any

import numpy as np

from pyMEA.gradient.Gradient import Gradient
from pyMEA.gradient.Solver import Solver
from pyMEA.read.model.MEA import MEA


class Gradients:
    def __init__(self, data: MEA, peak_index, ele_dis=450, mesh_num=100) -> None:
        self.gradients: list[Gradient] = []
        times, remove_ch = remove_undetected_ch(data, peak_index)

        # 全拍動周期について勾配を計算していく
        for time in times:
            solver = Solver(time, remove_ch, ele_dis, mesh_num)
            self.gradients.append(Gradient(solver))
        pass

    def __repr__(self) -> list[Gradient]:
        return repr(self.gradients)

    def __getitem__(self, index: int) -> Gradient:
        return self.gradients[index]

    def __len__(self) -> int:
        return len(self.gradients)

    @property
    def r2s(self) -> list[float]:
        return [grad.r2 for grad in self.gradients]

    def calc_velocity(self) -> list[np.ndarray[float]]:
        cvs = []
        for gradient in self.gradients:
            cvs.append(gradient.calc_velocity())
        return cvs

    def draw_2d(
        self,
        contour=False,
        isQuiver=True,
        xlabel="X (μm)",
        ylabel="Y (μm)",
        clabel="Δt (ms)",
        dpi=300,
        cmap="jet",
    ) -> None:
        for gradient in self.gradients:
            gradient.draw2d(contour, isQuiver, xlabel, ylabel, clabel, dpi, cmap)

    def draw_3d(
        self,
        xlabel="",
        ylabel="",
        clabel="",
        dpi=300,
    ) -> None:
        for gradient in self.gradients:
            gradient.draw_3d(xlabel, ylabel, clabel, dpi)


def remove_undetected_ch(
    data: MEA, peak_index: np.ndarray
) -> tuple[list[list[np.ndarray[Any, Any]]], list[int]]:
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

    times = []
    for j in range(len(time[0])):
        times.append([time[i][j] for i in range(len(time))])

    return times, remove_ch
