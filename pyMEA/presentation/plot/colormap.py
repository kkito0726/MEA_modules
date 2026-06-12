"""伝導解析カラーマップ描画 (2D・3D・ライン状ネットワーク)。

FigMEAの同名メソッドから呼び出される実装本体。
"""

import io

from pyMEA.domain.model.Electrode import Electrode
from pyMEA.domain.model.MEA import MEA
from pyMEA.domain.model.peak_model import Peaks64
from pyMEA.domain.service.gradient.Gradient import Gradient
from pyMEA.domain.service.gradient.Gradients import Gradients
from pyMEA.domain.service.gradient.Solver import Solver
from pyMEA.domain.service.peak_detection import detect_peak_neg
from pyMEA.domain.service.peak_times import (
    remove_undetected_ch,
    remove_undetected_ch_from64ch,
)
from pyMEA.presentation.plot.plot import draw_line, draw_line_conduction
from pyMEA.presentation.video import VideoMEA


def draw_2d(
    data: MEA,
    electrode: Electrode,
    peak_index: Peaks64,
    base_ch: int | None = None,
    mesh_num=100,
    contour=False,
    isQuiver=True,
    dpi=300,
    cmap="jet",
    isBuf=False,
) -> VideoMEA | list[Gradient]:
    """
    2Dカラーマップ描画
    """
    if base_ch:
        # 基準電極が指定されていたらその電極の拍動周期ごとにピーク抽出する
        result = []
        for divided_data in data.from_beat_cycles(peak_index, base_ch):
            peak = detect_peak_neg(divided_data)
            times, remove_ch = remove_undetected_ch_from64ch(data, peak)
            grad = Gradient(Solver(times[0], remove_ch, electrode.ele_dis, mesh_num))
            buf: io.BytesIO = grad.draw2d(contour, isQuiver, dpi=dpi, cmap=cmap, isBuf=isBuf)

            if isBuf:
                result.append(buf)
            else:
                result.append(grad)
        if isBuf:
            # list[BytesIO]を渡してもlist[FigImage]にキャストされる
            return VideoMEA(result)
        else:
            return result

    else:
        grads = Gradients(data, peak_index, electrode.ele_dis, mesh_num)
        buf_list = grads.draw_2d(contour, isQuiver, dpi=dpi, cmap=cmap, isBuf=isBuf)

        if isBuf:
            return VideoMEA(buf_list)
        else:
            return grads.gradients


def draw_3d(
    data: MEA,
    electrode: Electrode,
    peak_index: Peaks64,
    mesh_num=100,
    xlabel="X (μm)",
    ylabel="Y (μm)",
    clabel="Δt (ms)",
    dpi=300,
    isBuf=False,
) -> VideoMEA | Gradients:
    """
    3Dカラーマップ描画
    """
    grads = Gradients(data, peak_index, electrode.ele_dis, mesh_num)
    buf_list = grads.draw_3d(xlabel, ylabel, clabel, dpi, isBuf=isBuf)

    if isBuf:
        return VideoMEA(buf_list)
    else:
        return grads


def draw_line_conduction_map(
    data: MEA,
    electrode: Electrode,
    peak_index: Peaks64,
    amc_chs: list[int],
    base_ch: int | None = None,
    isLoop=True,
    dpi=300,
    isBuf=False,
) -> VideoMEA | None:
    """
    ライン状心筋細胞ネットワークのカラーマップ描画
    """
    if base_ch:
        # 基準電極が指定されていたらその電極の拍動周期ごとにピーク抽出する
        if base_ch not in amc_chs:
            raise ValueError("基準電極はAMC内の電極から選択してください")

        result = []
        for divided_data in data.from_beat_cycles(peak_index, base_ch):
            peak = detect_peak_neg(divided_data)
            times, remove_ch_index = remove_undetected_ch(divided_data, peak, amc_chs)
            result.append(
                draw_line(
                    times[0],
                    amc_chs,
                    remove_ch_index,
                    electrode,
                    isLoop,
                    dpi,
                    isBuf=isBuf,
                )
            )
        if isBuf:
            return VideoMEA(result)
    else:
        buf_list = draw_line_conduction(
            data, electrode, peak_index, amc_chs, isLoop, dpi, isBuf=isBuf
        )

        if isBuf:
            return VideoMEA(buf_list)
