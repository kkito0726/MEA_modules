"""勾配解析結果 (Gradient) のカラーマップ描画実装。

ドメイン層にmatplotlib依存を持ち込まないため、描画ロジックはここに置く。
Gradient.draw2d() / Gradient.draw_3d() から遅延importで呼び出される。
"""

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from pyMEA.constants import ELECTRODE_GRID_SIZE
from pyMEA.domain.service.gradient.Gradient import grad_model, grad_velocity
from pyMEA.domain.service.gradient.Solver import Solver
from pyMEA.presentation.output import output_buf

if TYPE_CHECKING:
    from pyMEA.domain.service.gradient.Gradient import Gradient


@output_buf
def draw_gradient_2d(
    gradient: "Gradient",
    contour=False,
    isQuiver=True,
    xlabel="X (μm)",
    ylabel="Y (μm)",
    clabel="Δt (ms)",
    dpi=300,
    cmap="jet",
    isBuf=False,
):
    solver = gradient.solver

    # グラフにプロットする
    fig = plt.figure(dpi=dpi)
    ax = fig.add_subplot(111)
    ax.set_aspect("equal", adjustable="box")
    if contour:
        c = ax.contourf(
            solver.xx,
            solver.yy,
            solver.z.reshape(solver.mesh_num, solver.mesh_num),
            cmap=cmap,
        )
        ax.contour(
            solver.xx,
            solver.yy,
            solver.z.reshape(100, 100),
            colors="k",
            linewidths=0.5,
            linestyles="solid",
        )
    else:
        c = ax.pcolormesh(
            solver.xx,
            solver.yy,
            solver.z.reshape(solver.mesh_num, solver.mesh_num),
            cmap=cmap,
        )
    # 電極上に速度ベクトルを描画
    ele_solver = Solver(
        solver.time, solver.remove_ch, solver.ele_dis, ELECTRODE_GRID_SIZE
    )
    ele_grad_x, ele_grad_y = grad_model((ele_solver.xx, ele_solver.yy), *ele_solver.popt)
    ele_vx, ele_vy = grad_velocity(ele_grad_x, ele_grad_y)

    plt.scatter(ele_solver.xx, ele_solver.yy, marker=",", color="grey")
    if isQuiver:
        plt.quiver(ele_solver.xx, ele_solver.yy, ele_vx, ele_vy)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    bar = plt.colorbar(c)
    bar.set_label(clabel)
    plt.xticks(np.arange(0, solver.ele_dis * 7 + 1, solver.ele_dis))
    plt.yticks(np.arange(0, solver.ele_dis * 7 + 1, solver.ele_dis))


@output_buf
def draw_gradient_3d(
    gradient: "Gradient", xlabel="", ylabel="", clabel="", dpi=300, isBuf=False
):
    solver = gradient.solver

    fig = plt.figure(dpi=dpi)
    ax = fig.add_subplot(111, projection="3d")
    c = ax.plot_surface(
        solver.xx,
        solver.yy,
        solver.z.reshape(solver.mesh_num, solver.mesh_num),
        cmap="jet",
    )
    bar = fig.colorbar(c)
    bar.set_label(clabel)
    plt.xticks(np.arange(0, solver.ele_dis * 7 + 1, solver.ele_dis))
    plt.yticks(np.arange(0, solver.ele_dis * 7 + 1, solver.ele_dis))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
