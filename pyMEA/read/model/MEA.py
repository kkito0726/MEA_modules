from dataclasses import dataclass
from functools import cached_property
from typing import Any

from numpy import append, empty, float64, linspace, ndarray, pad
from numpy._typing import NDArray
from scipy.signal import filtfilt, iirnotch

from pyMEA.find_peaks.peak_model import Peaks64
from pyMEA.read.model.HedPath import HedPath


@dataclass(frozen=True)
class MEA:
    """
    MEA計測データの読み込み
    ----------
    Args:
        hed_path: ヘッダーファイルのパス
        start: 読み込み開始時間 (s)
        end: 読み込み終了時間 (s)
    """

    hed_path: HedPath
    start: int | float
    end: int | float
    SAMPLING_RATE: int
    GAIN: int
    array: NDArray[float64]

    def __post_init__(self):
        self.array.setflags(write=False)
        # self.array に対して副作用を与えないようコピーして freeze
        object.__setattr__(self, "array", self._freeze_array(self.array.copy()))

    @staticmethod
    def _freeze_array(arr) -> ndarray[Any]:
        arr.setflags(write=False)
        return arr

    @cached_property
    def time(self):
        return self.end - self.start

    def __repr__(self):
        return repr(self.array)

    def __getitem__(self, index: int) -> ndarray:
        return self.array[index]

    def __len__(self) -> int:
        return len(self.array)

    def __iter__(self):
        return iter(self.array)

    def __add__(self, value):
        return self.array + value

    def __sub__(self, value):
        return self.array - value

    def __mul__(self, value):
        return self.array * value

    def __truediv__(self, value):
        return self.array / value

    def __floordiv__(self, value):
        return self.array // value

    @property
    def info(self) -> str:
        info = (
            f"読み込み開始時間  : {self.start} s\n"
            f"読み込み終了時間  : {self.end} s\n"
            f"読み込み合計時間  : {self.time} s\n"
            f"サンプリングレート: {self.SAMPLING_RATE} Hz\n"
            f"GAIN           : {self.GAIN}"
        )
        print(info)
        return info

    @property
    def shape(self) -> tuple[int, ...]:
        return self.array.shape

    def from_slice(self, start_frame: int | float, end_frame: int | float):
        return MEA(
            self.hed_path,
            start_frame / self.SAMPLING_RATE + self.start,
            end_frame / self.SAMPLING_RATE + self.start,
            self.SAMPLING_RATE,
            self.GAIN,
            self.array[:, int(start_frame) : int(end_frame)],
        )

    def from_beat_cycles(
        self, peak_index: Peaks64, base_ch: int, margin_time: float = 0.25
    ):
        """
        拍動周期ごとのデータに分割してMEAクラスのリストとして返す
        Parameters
        ----------
        peak_index: 読み込みデータ全体のピーク抽出結果
        base_ch: 基準電極
        margin_time: ピークの前後何秒を拍動周期とするか

        Returns list[MEA]
        -------

        """
        result: list[MEA] = []
        half_window = int(margin_time * self.SAMPLING_RATE)
        base_peaks = peak_index[base_ch]
        total_frames = self.array.shape[1]

        for peak in base_peaks:
            start = max(0, peak - half_window)
            end = min(total_frames, peak + half_window)
            result.append(self.from_slice(start, end))

        return result

    def init_time(self):
        """時刻データを0 (s)からにしたMEAインスタンスを返却"""
        t = self.array[0] - self.array[0][0]
        t = t.reshape(1, len(t))
        new_array = append(t, self.array[1:], axis=0)

        return MEA(
            self.hed_path,
            start=0,
            end=len(new_array[0]) / self.SAMPLING_RATE,
            SAMPLING_RATE=self.SAMPLING_RATE,
            GAIN=self.GAIN,
            array=new_array,
        )

    def down_sampling(self, down_sampling_rate=100):
        new_voltages = [
            downsample_max_min(self.array[i], down_sampling_rate * 2)
            for i in range(1, 65)
        ]
        new_sampling_rate = int(self.SAMPLING_RATE / down_sampling_rate)
        end = len(new_voltages[0]) / new_sampling_rate

        t = linspace(self.start, end, int((end - self.start) * new_sampling_rate))
        t = t.reshape(1, len(t))
        new_array = append(t, new_voltages, axis=0)

        return MEA(
            self.hed_path,
            self.start,
            t[0][-1],
            new_sampling_rate,
            self.GAIN,
            new_array,
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
        filtered : MEA
            フィルタ後の信号
        """
        new_voltages = [
            iirnotch_filter_single_ch(self.array[ch], self.SAMPLING_RATE, filter_hz, Q)
            for ch in range(1, 65)
        ]
        t = self.array[0]
        t = t.reshape(1, len(t))
        new_array = append(t, new_voltages, axis=0)

        return MEA(
            self.hed_path,
            self.start,
            self.array[0][-1],
            self.SAMPLING_RATE,
            self.GAIN,
            new_array,
        )


def iirnotch_filter_single_ch(signal, fs, f0=50, Q=30):
    """
    IIRノッチフィルタで特定周波数のノイズを除去する関数

    Parameters
    ----------
    signal : array_like
        入力信号（1次元配列）
    fs : float
        サンプリング周波数 [Hz]
    f0 : float, optional
        除去したい周波数（デフォルト 50 Hz）
    Q : float, optional
        Q値（ノッチの鋭さ、デフォルト 30）

    Returns
    -------
    filtered : ndarray
        フィルタ後の信号
    """
    # ノッチフィルタ設計
    b, a = iirnotch(f0, Q, fs)

    # 前後方向フィルタ（位相歪み補正）
    filtered = filtfilt(b, a, signal)

    return filtered


def downsample_max_min(arr: NDArray[float64], factor: int) -> NDArray[float64]:
    """
    Max-min ダウンサンプリング（NumPyベース）

    Args:
        arr (np.ndarray): 1次元の波形データ
        factor (int): ダウンサンプリング率（1フレームあたりの元データ数）

    Returns:
        np.ndarray: ダウンサンプリングされた波形データ（[min0, max0, min1, max1, ...] 形式）
    """
    n = len(arr)

    # factor で割り切れない場合に備え、末尾を繰り返しで padding して帳尻を合わせる
    pad_len = (factor - (n % factor)) % factor
    padded = pad(arr, (0, pad_len), mode="edge")

    # データを [N // factor, factor] の2次元に reshape（各ブロックに分割）
    reshaped = padded.reshape(-1, factor)

    # 各ブロックの最小値・最大値を計算（列方向）
    min_vals = reshaped.min(axis=1)
    max_vals = reshaped.max(axis=1)

    # min, max を交互に interleave（視覚的品質を保つ）
    result = empty(min_vals.size + max_vals.size, dtype=arr.dtype)
    result[0::2] = min_vals
    result[1::2] = max_vals

    return result
