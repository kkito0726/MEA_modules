from dataclasses import dataclass

import matplotlib.pyplot as plt

from pyMEA.calculator.values.AbstractValues import AbstractValues
from pyMEA.find_peaks.peak_model import NegPeaks, PosPeaks
from pyMEA.read.model.MEA import MEA
from pyMEA.utils.decorators import output_buf


@dataclass(frozen=True)
class FPD(AbstractValues):
    ch: int
    data: MEA
    neg_peaks: NegPeaks
    pos_peaks: PosPeaks

    @output_buf
    def show(
        self,
        start: int = None,
        end: int = None,
        volt_min=None,
        volt_max=None,
        dpi=None,
        isBuf=False,
    ) -> None:
        plt.figure(dpi=dpi)

        plt.plot(self.data[0], self.data[self.ch])
        plt.plot(
            self.data[0][self.neg_peaks], self.data[self.ch][self.neg_peaks], ".", c="r"
        )
        plt.plot(
            self.data[0][self.pos_peaks], self.data[self.ch][self.pos_peaks], ".", c="r"
        )

        if start is not None and end is not None:
            plt.xlim(start, end)

        if volt_min is not None and volt_max is not None:
            plt.ylim(volt_min, volt_max)

        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (μV)")
