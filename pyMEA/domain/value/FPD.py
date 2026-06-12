from dataclasses import dataclass

from pyMEA.domain.model.MEA import MEA
from pyMEA.domain.model.peak_model import NegPeaks, PosPeaks
from pyMEA.domain.value.AbstractValues import AbstractValues


@dataclass(frozen=True)
class FPD(AbstractValues):
    ch: int
    data: MEA
    neg_peaks: NegPeaks
    pos_peaks: PosPeaks

    def show(
        self,
        start: int = None,
        end: int = None,
        volt_min=None,
        volt_max=None,
        dpi=None,
        isBuf=False,
    ):
        # 描画はpresentation層に委譲する
        # (domainのimport時にmatplotlibを読み込まないよう遅延import)
        from pyMEA.presentation.value_plots import show_fpd

        return show_fpd(
            self,
            start=start,
            end=end,
            volt_min=volt_min,
            volt_max=volt_max,
            dpi=dpi,
            isBuf=isBuf,
        )
