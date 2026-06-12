"""ドメイン値オブジェクト (ISI, FPD) の描画実装。

ドメイン層にmatplotlib依存を持ち込まないため、描画ロジックはここに置く。
ISI.show() / FPD.show() から遅延importで呼び出される。
"""

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from pyMEA.presentation.output import output_buf

if TYPE_CHECKING:
    from pyMEA.domain.value.FPD import FPD
    from pyMEA.domain.value.ISI import ISI


@output_buf
def show_isi(
    isi: "ISI",
    start: int = None,
    end: int = None,
    volt_min=None,
    volt_max=None,
    dpi=None,
    isBuf=False,
) -> None:
    plt.figure(dpi=dpi)

    plt.plot(isi.data[0], isi.data[isi.ch])
    plt.plot(isi.data[0][isi.peaks], isi.data[isi.ch][isi.peaks], ".", c="r")

    if start is not None and end is not None:
        plt.xlim(start, end)

    if volt_min is not None and volt_max is not None:
        plt.ylim(volt_min, volt_max)

    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (μV)")


@output_buf
def show_fpd(
    fpd: "FPD",
    start: int = None,
    end: int = None,
    volt_min=None,
    volt_max=None,
    dpi=None,
    isBuf=False,
) -> None:
    plt.figure(dpi=dpi)

    plt.plot(fpd.data[0], fpd.data[fpd.ch])
    plt.plot(fpd.data[0][fpd.neg_peaks], fpd.data[fpd.ch][fpd.neg_peaks], ".", c="r")
    plt.plot(fpd.data[0][fpd.pos_peaks], fpd.data[fpd.ch][fpd.pos_peaks], ".", c="r")

    if start is not None and end is not None:
        plt.xlim(start, end)

    if volt_min is not None and volt_max is not None:
        plt.ylim(volt_min, volt_max)

    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (μV)")
