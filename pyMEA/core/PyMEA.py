from dataclasses import dataclass

from numpy import ndarray

from pyMEA import Calculator, FigMEA
from pyMEA.core.Electrode import Electrode
from pyMEA.read.model.MEA import MEA


@dataclass(frozen=True)
class PyMEA:
    data: MEA
    electrode: Electrode
    fig: FigMEA
    calculator: Calculator

    def __repr__(self):
        return repr(self.data.array)

    def __getitem__(self, index: int) -> ndarray:
        return self.data.array[index]

    def __len__(self) -> int:
        return len(self.data.array)

    def __iter__(self):
        return iter(self.data.array)

    def __add__(self, value):
        return self.data.array + value

    def __sub__(self, value):
        return self.data.array - value

    def __mul__(self, value):
        return self.data.array * value

    def __truediv__(self, value):
        return self.data.array / value

    def __floordiv__(self, value):
        return self.data.array // value
