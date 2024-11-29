from pyMEA.read.MEA import MEA
from pyMEA.utils.filter import filter_by_moving_average


class FilterMEA(MEA):
    def __init__(
        self,
        hed_path: str,
        start: int = 0,
        end: int = 120,
        power_noise_freq=50,
        steps=10,
    ) -> None:
        super().__init__(hed_path, start, end)
        self.power_noise_freq = power_noise_freq
        self.steps = steps
        self._array = filter_by_moving_average(self, power_noise_freq, steps)
