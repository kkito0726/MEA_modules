from dataclasses import dataclass

from numpy import ndarray

from pyMEA import Calculator, FigMEA
from pyMEA.core.Electrode import Electrode
from pyMEA.find_peaks.peak_model import Peaks64
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

    def from_slice(self, start: int | float, end: int | float):
        start_frame, end_frame = (
            int((start - self.data.start) * self.data.SAMPLING_RATE),
            int((end - self.data.start) * self.data.SAMPLING_RATE),
        )
        new_data = self.data.from_slice(start_frame, end_frame)
        return PyMEA(
            new_data,
            self.electrode,
            FigMEA(new_data, self.electrode),
            Calculator(new_data, self.electrode.ele_dis),
        )

    def from_beat_cycles(
        self, peak_index: Peaks64, base_ch: int, margin_time: float = 0.25
    ):
        new_data_list = self.data.from_beat_cycles(peak_index, base_ch, margin_time)
        return [
            PyMEA(
                new_data,
                self.electrode,
                FigMEA(new_data, self.electrode),
                Calculator(new_data, self.electrode.ele_dis),
            )
            for new_data in new_data_list
        ]

    def init_time(self):
        """時刻データを0 (s)からにしたMEAインスタンスを返却"""
        new_data = self.data.init_time()
        return PyMEA(
            new_data,
            self.electrode,
            FigMEA(new_data, self.electrode),
            Calculator(new_data, self.electrode.ele_dis),
        )

    def down_sampling(self, down_sampling_rate=100):
        new_data = self.data.down_sampling(down_sampling_rate)
        return PyMEA(
            new_data,
            self.electrode,
            FigMEA(new_data, self.electrode),
            Calculator(new_data, self.electrode.ele_dis),
        )

    def iirnotch_filter(self, filter_hz=50, Q=30):
        """
        IIRノッチフィルタで特定周波数のノイズを除去する関数

        Parameters
        ----------
        filter_hz : float, optional
            除去したい周波数（デフォルト 50 Hz）
        Q : float, optional
            Q値（ノッチの鋭さ、デフォルト 30）

        Returns
        -------
        filtered : PyMEA
            フィルタ後の信号
        """
        new_data = self.data.iirnotch_filter(filter_hz, Q)
        return PyMEA(
            new_data,
            self.electrode,
            FigMEA(new_data, self.electrode),
            Calculator(new_data, self.electrode.ele_dis),
        )
