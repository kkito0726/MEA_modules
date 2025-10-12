from dataclasses import dataclass

from pyMEA.calculator.values.AbstractValues import AbstractValues
from pyMEA.find_peaks.peak_model import Peaks64
from pyMEA.read.model.MEA import MEA


@dataclass(frozen=True)
class ConductionVelocity(AbstractValues):
    ch1: int
    ch2: int
    distance: float
    data: MEA
    peaks64: Peaks64
