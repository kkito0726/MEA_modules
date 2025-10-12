from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AbstractValues:
    values: np.ndarray

    def __repr__(self):
        return repr(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def __add__(self, value):
        return self.values + value

    def __sub__(self, value):
        return self.values - value

    def __mul__(self, value):
        return self.values * value

    def __truediv__(self, value):
        return self.values / value

    def __floordiv__(self, value):
        return self.values // value

    def __eq__(self, other):
        if isinstance(other, AbstractValues):
            return np.array_equal(self.values, other.values)
        return False

    def __ne__(self, other):
        return self.values != other

    def __lt__(self, other):
        return self.values < other

    def __le__(self, other):
        return self.values <= other

    def __gt__(self, other):
        return self.values > other

    def __ge__(self, other):
        return self.values >= other

    @property
    def mean(self):
        return np.mean(self.values)

    @property
    def std(self):
        return np.std(self.values)

    @property
    def se(self):
        return self.std / len(self.values)

    @property
    def stv(self):
        diff = abs(np.diff(self.values))
        N2 = len(diff) * np.sqrt(2)
        return sum(diff) / N2

    @property
    def coefficient_of_variation(self):
        return np.std(self.values) / np.mean(self.values) * 100
