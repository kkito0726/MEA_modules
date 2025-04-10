from dataclasses import dataclass

import matplotlib.pyplot as plt
from numpy import array_equal, ndarray

from pyMEA.find_peaks.peak_model import NegPeaks, PosPeaks
from pyMEA.read.MEA import MEA


@dataclass(frozen=True)
class FPD:
    ch: int
    neg_peaks: NegPeaks
    pos_peaks: PosPeaks
    fpds: ndarray

    def __repr__(self):
        return repr(self.fpds)

    def __getitem__(self, item):
        return self.fpds[item]

    def __len__(self):
        return len(self.fpds)

    def __add__(self, value):
        return self.fpds + value

    def __sub__(self, value):
        return self.fpds - value

    def __mul__(self, value):
        return self.fpds * value

    def __truediv__(self, value):
        return self.fpds / value

    def __floordiv__(self, value):
        return self.fpds // value

    def __eq__(self, other):
        if isinstance(other, FPD):
            return array_equal(self.fpds, other.fpds)
        return False

    def __ne__(self, other):
        return self.fpds != other

    def __lt__(self, other):
        return self.fpds < other

    def __le__(self, other):
        return self.fpds <= other

    def __gt__(self, other):
        return self.fpds > other

    def __ge__(self, other):
        return self.fpds >= other

    def show(
        self,
        data: MEA,
        start: int = None,
        end: int = None,
        volt_min=None,
        volt_max=None,
        dpi=None,
    ) -> None:
        plt.figure(dpi=dpi)

        plt.plot(data[0], data[self.ch])
        plt.plot(data[0][self.neg_peaks], data[self.ch][self.neg_peaks], ".", c="r")
        plt.plot(data[0][self.pos_peaks], data[self.ch][self.pos_peaks], ".", c="r")

        if start is not None and end is not None:
            plt.xlim(start, end)

        if volt_min is not None and volt_max is not None:
            plt.ylim(volt_min, volt_max)

        plt.show()
