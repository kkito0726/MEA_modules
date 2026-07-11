from dataclasses import dataclass

from numpy import ndarray

from pyMEA.domain.service.calculator import Calculator
from pyMEA.domain.model.Electrode import Electrode
from pyMEA.presentation.FigMEA import FigMEA
from pyMEA.domain.model.peak_model import Peaks64
from pyMEA.domain.model.MEA import MEA


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

    def save_npz(self, path: str, dtype: str = "int16") -> None:
        """計測データを .npz(圧縮)で保存する。

        Parameters
        ----------
        path : str
            保存先パス(.npz)
        dtype : str
            "int16"(既定, 16bit量子化, 約1/4。誤差は測定分解能以下) /
            "float32"(ビット完全一致, 約1/2)
        """
        from pyMEA.infrastructure.npz_io import save_mea_npz

        save_mea_npz(self.data, path, dtype, self.electrode.ele_dis)

    def _rebuild(self, new_data: MEA) -> "PyMEA":
        """変換後のMEAデータから各責務クラスを再構築したPyMEAを返す"""
        return PyMEA(
            new_data,
            self.electrode,
            FigMEA(new_data, self.electrode),
            Calculator(new_data, self.electrode.ele_dis),
        )

    def from_slice(self, start: int | float, end: int | float):
        start_frame, end_frame = (
            int((start - self.data.start) * self.data.SAMPLING_RATE),
            int((end - self.data.start) * self.data.SAMPLING_RATE),
        )
        return self._rebuild(self.data.from_slice(start_frame, end_frame))

    def from_beat_cycles(
        self, peak_index: Peaks64, base_ch: int, margin_time: float = 0.25
    ):
        new_data_list = self.data.from_beat_cycles(peak_index, base_ch, margin_time)
        return [self._rebuild(new_data) for new_data in new_data_list]

    def init_time(self):
        """時刻データを0 (s)からにしたMEAインスタンスを返却"""
        return self._rebuild(self.data.init_time())

    def down_sampling(self, down_sampling_rate=100):
        return self._rebuild(self.data.down_sampling(down_sampling_rate))

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
        return self._rebuild(self.data.iirnotch_filter(filter_hz, Q))

    def highpass(self, cutoff=1, order=4):
        """
        ハイパスフィルタ（ゼロ位相 Butterworth）でベースラインドリフトを除去する。

        fig・calculator もデノイズ後のデータで再構築した PyMEA を返すため、
        そのまま描画・数値計算に使える（ピークタイミングは不変）。

        Parameters
        ----------
        cutoff : float, optional
            下限カットオフ周波数 [Hz]（デフォルト 1 Hz）
        order : int, optional
            フィルタ次数（デフォルト 4）

        Returns
        -------
        PyMEA
            フィルタ後の新しいインスタンス
        """
        return self._rebuild(self.data.highpass(cutoff, order))

    def bandpass(self, low, high, order=4):
        """
        バンドパスフィルタ（ゼロ位相 Butterworth）で指定帯域のみ通す。

        fig・calculator もデノイズ後のデータで再構築した PyMEA を返すため、
        そのまま描画・数値計算に使える（ピークタイミングは不変）。

        Parameters
        ----------
        low : float
            下限カットオフ周波数 [Hz]
        high : float
            上限カットオフ周波数 [Hz]
        order : int, optional
            フィルタ次数（デフォルト 4）

        Returns
        -------
        PyMEA
            フィルタ後の新しいインスタンス
        """
        return self._rebuild(self.data.bandpass(low, high, order))

    def common_median_reference(self):
        """
        各時刻で全電極の中央値を減算し、電極間で共通するノイズ（電源・参照ドリフト等）を除去する。

        fig・calculator もデノイズ後のデータで再構築した PyMEA を返す。

        Returns
        -------
        PyMEA
            ノイズ除去後の新しいインスタンス
        """
        return self._rebuild(self.data.common_median_reference())

    def wavelet_denoise(self, wavelet="db4", level=None):
        """
        ウェーブレット縮退で帯域内の広帯域ノイズを除去する（スパイク形状を保持）。

        fig・calculator もデノイズ後のデータで再構築した PyMEA を返す。

        Parameters
        ----------
        wavelet : str, optional
            ウェーブレット母関数（デフォルト "db4"）
        level : int | None, optional
            分解レベル。None なら信号長から自動決定（最大6）

        Returns
        -------
        PyMEA
            デノイズ後の新しいインスタンス

        Notes
        -----
        微弱信号では弱いスパイクごと削るおそれがあるため、検出率を確認すること。
        """
        return self._rebuild(self.data.wavelet_denoise(wavelet, level))
