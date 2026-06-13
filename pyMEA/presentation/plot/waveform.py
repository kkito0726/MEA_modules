"""波形描画 (全電極・単一電極・ピーク重畳・スペクトラム)。

FigMEAの同名メソッドから呼び出される実装本体。
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch

from pyMEA.constants import ELECTRODE_GRID_SIZE
from pyMEA.domain.model.MEA import MEA
from pyMEA.domain.model.peak_model import Peaks64
from pyMEA.presentation.output import channel, output_buf
from pyMEA.presentation.plot.color import normalize_color


@channel
@output_buf
def plot_spectrum(
    data: MEA, ch: int, max_freq=500, nperseg=2048, figsize=(10, 4), dpi=100, isBuf=False
):
    """
    与えられた信号のスペクトルをプロットする関数
    - FFTの振幅スペクトル
    """
    N = len(data[ch])

    # === FFT ===
    fft_vals = np.fft.rfft(data[ch])
    fft_freq = np.fft.rfftfreq(N, 1 / data.SAMPLING_RATE)
    amplitude = np.abs(fft_vals) / N

    # === Welch ===
    f, Pxx = welch(data[ch], fs=data.SAMPLING_RATE, nperseg=nperseg)

    # === プロット ===
    plt.figure(figsize=figsize, dpi=dpi)

    # FFT
    plt.plot(fft_freq, amplitude)
    plt.xlim(0, max_freq)
    plt.xticks(np.arange(0, max_freq + 50, 50))
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.grid()

    plt.tight_layout()


@output_buf
def show_all(
    data: MEA,
    start=None,
    end=5,
    volt_min=-200,
    volt_max=200,
    figsize=(8, 8),
    dpi=300,
    color: list[str] | list[list[float]] = None,
    isBuf=False,
):
    """
    64電極すべての波形を描画する
    """
    # 時間の設定がない場合はデータの最初から5秒間をプロットする。
    if start is None:
        start = data.start
    if end is None:
        end = start + 5

    # 読み込み開始時間が0ではないときズレが生じるため差を取っている
    start_frame = int(abs(data.start - start) * data.SAMPLING_RATE)
    end_frame = int(abs(data.start - end) * data.SAMPLING_RATE)

    x = data[0][start_frame:end_frame]

    color = normalize_color(color)

    fig, axes = plt.subplots(
        ELECTRODE_GRID_SIZE, ELECTRODE_GRID_SIZE, figsize=figsize, dpi=dpi
    )
    color_index = 0
    for i, ax in enumerate(axes.flat):
        if color is None:
            # 配色指定あり
            ax.plot(x, data.array[i + 1][start_frame:end_frame])
        else:
            # 配色指定なし
            ax.plot(
                x,
                data.array[i + 1][start_frame:end_frame],
                color=color[color_index],
            )
            color_index += 1
            if color_index >= len(color):
                color_index = 0
        ax.set_ylim(volt_min, volt_max)


@channel
@output_buf
def show_single(
    data: MEA,
    ch: int,
    start: int,
    end: int,
    volt_min=-200,
    volt_max=200,
    figsize=(8, 2),
    dpi=None,
    xlabel="Time (s)",
    ylabel="Voltage (μV)",
    color: str = None,
    isBuf=False,
):
    """
    1電極の波形を描画する
    """
    # 読み込み開始時間が0ではないときズレが生じるため差を取っている
    start_frame = int(abs(data.start - start) * data.SAMPLING_RATE)
    end_frame = int(abs(data.start - end) * data.SAMPLING_RATE)

    plt.figure(figsize=figsize, dpi=dpi)
    plt.plot(
        data[0][start_frame:end_frame],
        data.array[ch][start_frame:end_frame],
        color=color,
    )
    plt.xlim(start, end)
    plt.ylim(volt_min, volt_max)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


@channel
@output_buf
def plot_peaks(
    data: MEA,
    ch: int,
    *peak_indexes: Peaks64,
    start: int,
    end: int,
    volt_min=-200,
    volt_max=200,
    figsize=(8, 2),
    dpi=None,
    xlabel="Time (s)",
    ylabel="Voltage (μV)",
    color: str = None,
    peak_color: list[str] | list[list[float]] = None,
    isBuf=False,
):
    """
    1電極の波形とピークの位置をプロット
    """
    # 読み込み開始時間が0ではないときズレが生じるため差を取っている
    start_frame = int(abs(data.start - start) * data.SAMPLING_RATE)
    end_frame = int(abs(data.start - end) * data.SAMPLING_RATE)

    # 波形データのプロット
    plt.figure(figsize=figsize, dpi=dpi)
    x, y = (
        data[0][start_frame:end_frame],
        data.array[ch][start_frame:end_frame],
    )
    plt.plot(x, y, color=color)

    # ピークのプロット
    peak_color = normalize_color(peak_color, "red")
    peak_color_index = 0
    for peak_index in peak_indexes:
        peaks = peak_index[ch]
        peaks = peaks[start_frame < peaks]
        peaks = peaks[peaks < end_frame]
        plt.plot(x[peaks], y[peaks], ".", color=peak_color[peak_color_index])

        peak_color_index += 1
        if peak_color_index >= len(peak_color):
            peak_color_index = 0

    plt.xlim(start, end)
    plt.ylim(volt_min, volt_max)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
