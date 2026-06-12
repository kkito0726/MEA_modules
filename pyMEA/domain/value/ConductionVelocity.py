from dataclasses import dataclass

from pyMEA.domain.value.AbstractValues import AbstractValues
from pyMEA.domain.model.peak_model import Peaks64
from pyMEA.domain.model.MEA import MEA


@dataclass(frozen=True)
class ConductionVelocity(AbstractValues):
    ch1: int
    ch2: int
    distance: float
    data: MEA
    peaks64: Peaks64
