import statistics
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import numpy as np
from numpy import float64
from numpy._typing import NDArray

from pyMEA.find_peaks.peak_model import Peaks64
from pyMEA.gradient.Gradient import Gradient
from pyMEA.gradient.Solver import Solver
from pyMEA.read.model.MEA import MEA


@dataclass(frozen=True)
class Gradients:
    data: MEA
    peak_index: Peaks64
    ele_dis: int = 450
    mesh_num: int = 100
    times: NDArray[float64] = field(init=False)
    remove_ch: list[int] = field(init=False)

    def __post_init__(self):
        times, remove_ch = remove_undetected_ch(self.data, self.peak_index)
        object.__setattr__(self, "times", times)
        object.__setattr__(self, "remove_ch", remove_ch)

    @cached_property
    def gradients(self) -> list[Gradient]:
        # 全拍動周期について勾配を計算していく
        return [
            Gradient(Solver(time, self.remove_ch, self.ele_dis, self.mesh_num))
            for time in self.times
        ]

    def __repr__(self) -> list[Gradient]:
        return repr(self.gradients)

    def __getitem__(self, index: int) -> Gradient:
        return self.gradients[index]

    def __len__(self) -> int:
        return len(self.gradients)

    def __iter__(self):
        return iter(self.gradients)

    @cached_property
    def r2s(self) -> list[float]:
        return [grad.r2 for grad in self.gradients]

    def calc_velocity(self) -> list[NDArray[float64]]:
        return [gradient.calc_velocity() for gradient in self.gradients]

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
    data: MEA, peak_index: Peaks64
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
