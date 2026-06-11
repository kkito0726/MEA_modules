from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING

from numpy import float64
from numpy._typing import NDArray

from pyMEA.constants import DEFAULT_ELECTRODE_DISTANCE
from pyMEA.domain.model.MEA import MEA
from pyMEA.domain.model.peak_model import Peaks64
from pyMEA.domain.service.gradient.Gradient import Gradient
from pyMEA.domain.service.gradient.Solver import Solver
from pyMEA.domain.service.peak_times import remove_undetected_ch_from64ch

if TYPE_CHECKING:
    from pyMEA.presentation.FigImage import FigImage


@dataclass(frozen=True)
class Gradients:
    data: MEA
    peak_index: Peaks64
    ele_dis: int = DEFAULT_ELECTRODE_DISTANCE
    mesh_num: int = 100
    times: NDArray[float64] = field(init=False)
    remove_ch: list[int] = field(init=False)

    def __post_init__(self):
        times, remove_ch = remove_undetected_ch_from64ch(self.data, self.peak_index)
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
        isBuf=False,
    ) -> list | None:
        buf_list = [
            gradient.draw2d(contour, isQuiver, xlabel, ylabel, clabel, dpi, cmap, isBuf)
            for gradient in self.gradients
        ]

        if isBuf:
            return buf_list

    def draw_3d(
        self, xlabel="", ylabel="", clabel="", dpi=300, isBuf=False
    ) -> "list[FigImage] | None":
        buf_list: "list[FigImage | None]" = [
            gradient.draw_3d(xlabel, ylabel, clabel, dpi, isBuf=isBuf)
            for gradient in self.gradients
        ]
        if isBuf:
            return buf_list
