from dataclasses import dataclass, field
from functools import cached_property

import numpy as np
from numpy import float64
from numpy._typing import NDArray

from pyMEA.domain.service.gradient.Solver import Solver


@dataclass(frozen=True)
class Gradient:
    solver: Solver

    # 勾配ベクトル
    grad_x: NDArray[float64] = field(init=False)
    grad_y: NDArray[float64] = field(init=False)

    # 速度ベクトル
    vx: NDArray[float64] = field(init=False)
    vy: NDArray[float64] = field(init=False)

    def __post_init__(self):
        grad_x, grad_y = grad_model((self.solver.xx, self.solver.yy), *self.solver.popt)
        vx, vy = grad_velocity(grad_x, grad_y)

        object.__setattr__(self, "grad_x", self.solver.freeze_array(grad_x))
        object.__setattr__(self, "grad_y", self.solver.freeze_array(grad_y))
        object.__setattr__(self, "vx", self.solver.freeze_array(vx))
        object.__setattr__(self, "vy", self.solver.freeze_array(vy))

    @cached_property
    def r2(self) -> float:
        return self.solver.r2

    def calc_velocity(self) -> NDArray[float64]:
        return np.sqrt(self.vx**2 + self.vy**2).ravel() * 10**-6  # μm/s -> m/sに変換

    def draw2d(
        self,
        contour=False,
        isQuiver=True,
        xlabel="X (μm)",
        ylabel="Y (μm)",
        clabel="Δt (ms)",
        dpi=300,
        cmap="jet",
        isBuf=False,
    ):
        # 描画はpresentation層に委譲する
        # (domainのimport時にmatplotlibを読み込まないよう遅延import)
        from pyMEA.presentation.gradient_plots import draw_gradient_2d

        return draw_gradient_2d(
            self,
            contour=contour,
            isQuiver=isQuiver,
            xlabel=xlabel,
            ylabel=ylabel,
            clabel=clabel,
            dpi=dpi,
            cmap=cmap,
            isBuf=isBuf,
        )

    def draw_3d(self, xlabel="", ylabel="", clabel="", dpi=300, isBuf=False):
        # 描画はpresentation層に委譲する
        # (domainのimport時にmatplotlibを読み込まないよう遅延import)
        from pyMEA.presentation.gradient_plots import draw_gradient_3d

        return draw_gradient_3d(
            self, xlabel=xlabel, ylabel=ylabel, clabel=clabel, dpi=dpi, isBuf=isBuf
        )


def grad_model(
    X: tuple[NDArray[float64], NDArray[float64]],
    p00,
    p10,
    p01,
    p20,
    p11,
    p02,
    p30,
    p21,
    p12,
    p03,
) -> tuple[NDArray[float64], NDArray[float64]]:
    x, y = X
    grad_x = p10 + 2 * p20 * x + p11 * y + 3 * p30 * x**2 + 2 * p21 * x * y + p12 * y**2
    grad_y = p01 + p11 * x + 2 * p02 * y + p21 * x**2 + 2 * p12 * x * y + 3 * p03 * y**2
    return grad_x, grad_y


def grad_velocity(
    grad_x: NDArray[float64], grad_y: NDArray[float64]
) -> tuple[NDArray[float64], NDArray[float64]]:
    cx, cy = grad_x / (grad_x**2 + grad_y**2), grad_y / (grad_x**2 + grad_y**2)
    return cx, cy
