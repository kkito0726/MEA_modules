import io
from dataclasses import dataclass

import matplotlib.pyplot as plt

# from numpy import ndarray
import numpy as np
from scipy.signal import welch

from pyMEA.core.Electrode import Electrode
from pyMEA.figure.plot.histogram import mkHist
from pyMEA.figure.plot.plot import (
    draw_line,
    draw_line_conduction,
    remove_undetected_ch,
    showDetection,
)
from pyMEA.figure.plot.raster_plot import raster_plot
from pyMEA.figure.video import FigImage, VideoMEA
from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.find_peaks.peak_model import Peaks64
from pyMEA.gradient.Gradient import Gradient
from pyMEA.gradient.Gradients import Gradients, remove_undetected_ch_from64ch
from pyMEA.gradient.Solver import Solver
from pyMEA.read.model.MEA import MEA
from pyMEA.utils.decorators import channel, output_buf


@dataclass(frozen=True)
class FigMEA:
    data: MEA
    electrode: Electrode

    @channel
    @output_buf
    def plot_spectrum(
        self, ch: int, max_freq=500, nperseg=2048, figsize=(10, 4), dpi=100, isBuf=False
    ):
        """
        与えられた信号のスペクトルをプロットする関数
        - FFTの振幅スペクトル
        """
        N = len(self.data[ch])

        # === FFT ===
        fft_vals = np.fft.rfft(self.data[ch])
        fft_freq = np.fft.rfftfreq(N, 1 / self.data.SAMPLING_RATE)
        amplitude = np.abs(fft_vals) / N

        # === Welch ===
        f, Pxx = welch(self.data[ch], fs=self.data.SAMPLING_RATE, nperseg=nperseg)

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

    def _set_times(self, start, end) -> tuple[int, int]:
        # 時間の設定がなければ読み込み時間全体をプロットするようにする。
        if start is None:
            start = self.data.start
        if end is None:
            end = self.data.end

        return start, end

    @output_buf
    def showAll(
        self,
        start=None,
        end=5,
        volt_min=-200,
        volt_max=200,
        figsize=(8, 8),
        dpi=300,
        isBuf=False,
    ) -> FigImage | None:
        """
        64電極すべての波形を描画する

        Args:
            start: 読み込み開始時間 [s]
            end: 読み込み終了時間[s]
            volt_min: マイナス電位 [μV]
            volt_max: プラス電位 [μV]
            figsize: figのアスペクト比
            dpi: 解像度
            isBuf: グラフ画像を返すかどうか
        """
        # 時間の設定がない場合はデータの最初から5秒間をプロットする。
        if start is None:
            start = self.data.start
        if end is None:
            end = start + 5

        # 読み込み開始時間が0ではないときズレが生じるため差を取っている
        start_frame = int(abs(self.data.start - start) * self.data.SAMPLING_RATE)
        end_frame = int(abs(self.data.start - end) * self.data.SAMPLING_RATE)

        x = self.data.array[0][start_frame:end_frame]

        fig, axes = plt.subplots(8, 8, figsize=figsize, dpi=dpi)
        for i, ax in enumerate(axes.flat):
            ax.plot(
                x,
                self.data.array[i + 1][start_frame:end_frame],
            )
            ax.set_ylim(volt_min, volt_max)

    @channel
    @output_buf
    def showSingle(
        self,
        ch: int,
        start: int = None,
        end: int = None,
        volt_min=-200,
        volt_max=200,
        figsize=(8, 2),
        dpi=None,
        xlabel="Time (s)",
        ylabel="Voltage (μV)",
        isBuf=False,
    ) -> FigImage | None:
        """
        1電極の波形を描画する

        Args:
            ch: 描画する電極番号
            start: 読み込み開始時間 [s]
            end: 読み込み終了時間[s]
            volt_min: マイナス電位 [μV]
            volt_max: プラス電位 [μV]
            figsize: figのアスペクト比
            dpi: 解像度
            xlabel: X軸ラベル
            ylabel: Y軸ラベル
            isBuf: グラフ画像を返すかどうか
        """
        start, end = self._set_times(start, end)

        # 読み込み開始時間が0ではないときズレが生じるため差を取っている
        start_frame = int(abs(self.data.start - start) * self.data.SAMPLING_RATE)
        end_frame = int(abs(self.data.start - end) * self.data.SAMPLING_RATE)

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(
            self.data.array[0][start_frame:end_frame],
            self.data.array[ch][start_frame:end_frame],
        )
        plt.xlim(start, end)
        plt.ylim(volt_min, volt_max)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    @channel
    @output_buf
    def plotPeaks(
        self,
        ch: int,
        *peak_indexes: Peaks64,
        start: int = None,
        end: int = None,
        volt_min=-200,
        volt_max=200,
        figsize=(8, 2),
        dpi=None,
        xlabel="Time (s)",
        ylabel="Voltage (μV)",
        isBuf=False
    ) -> FigImage | None:
        """
        1電極の波形とピークの位置をプロット

        Args:
            ch: 描画する電極番号
            *peak_index: ピーク配列 (可変長)以降の引数は引数名を指定する
            start: 読み込み開始時間 [s]
            end: 読み込み終了時間[s]
            volt_min: マイナス電位 [μV]
            volt_max: プラス電位 [μV]
            figsize: figのアスペクト比
            dpi: 解像度
            xlabel: X軸ラベル
            ylabel: Y軸ラベル
            isBuf: グラフ画像を返すかどうか
        """
        start, end = self._set_times(start, end)

        # 読み込み開始時間が0ではないときズレが生じるため差を取っている
        start_frame = int(abs(self.data.start - start) * self.data.SAMPLING_RATE)
        end_frame = int(abs(self.data.start - end) * self.data.SAMPLING_RATE)

        # 波形データのプロット
        plt.figure(figsize=figsize, dpi=dpi)
        x, y = (
            self.data.array[0][start_frame:end_frame],
            self.data.array[ch][start_frame:end_frame],
        )
        plt.plot(x, y)

        # ピークのプロット
        for peak_index in peak_indexes:
            peaks = peak_index[ch]
            peaks = peaks[start_frame < peaks]
            peaks = peaks[peaks < end_frame]
            plt.plot(x[peaks], y[peaks], ".")

        plt.xlim(start, end)
        plt.ylim(volt_min, volt_max)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    def showDetection(
        self,
        eles: list[int],
        start=None,
        end=None,
        adjust_wave=200,
        figsize=(12, 12),
        xlabel="Time (s)",
        ylabel="Electrode Number",
        dpi=300,
        isBuf=False,
    ) -> FigImage | None:
        start, end = self._set_times(start, end)
        # 読み込み開始時間が途中からの場合のズレを解消する
        start = abs(start - self.data.start)
        end = abs(end - self.data.start)
        buf: FigImage = showDetection(
            MEA_raw=self.data,
            eles=eles,
            start=start,
            read_start=self.data.start,
            end=end,
            sampling_rate=self.data.SAMPLING_RATE,
            adjust_wave=adjust_wave,
            figsize=figsize,
            xlabel=xlabel,
            ylabel=ylabel,
            dpi=dpi,
            isBuf=isBuf,
        )
        return buf

    def raster_plot(
        self,
        peak_index: Peaks64,
        eles: list[int],
        tick_ch=1,
        figsize=(8, 8),
        start=None,
        end=None,
        dpi=300,
        isBuf=False,
    ) -> FigImage | None:
        start, end = self._set_times(start, end)
        return raster_plot(
            MEA_data=self.data,
            peak_index=peak_index,
            eles=eles,
            tick_ch=tick_ch,
            figsize=figsize,
            start=start,
            end=end,
            dpi=dpi,
            isBuf=isBuf,
        )

    def mkHist(
        self,
        peak_index: Peaks64,
        eles: list[int],
        figsize=(20, 6),
        bin_duration=0.05,
        start=None,
        end=None,
        y_max=None,
        dpi=300,
        isBuf=False,
    ) -> FigImage | np.ndarray:
        start, end = self._set_times(start, end)
        return mkHist(
            MEA_data=self.data,
            peak_index=peak_index,
            eles=eles,
            figsize=figsize,
            bin_duration=bin_duration,
            sampling=self.data.SAMPLING_RATE,
            start=start,
            end=end,
            y_max=y_max,
            dpi=dpi,
            isBuf=isBuf,
        )

    def draw_2d(
        self,
        peak_index: Peaks64,
        base_ch: int | None = None,
        mesh_num=100,  # mesh_num x mesh_numでデータを生成
        contour=False,  # 等高線で表示するかどうか
        isQuiver=True,  # 速度ベクトルを表示するかどうか
        dpi=300,
        cmap="jet",
        isBuf=False,
    ) -> VideoMEA | list[Gradient]:
        """
        2Dカラーマップ描画
        Args:
            peak_index: ピーク抽出結果
            base_ch: 基準電極
            mesh_num: mesh_num x mesh_numでデータを生成
            contour: 等高線で表示するかどうか
            isQuiver: 速度ベクトルを表示するかどうか
            dpi: 解像度
            cmap: カラーセット
            isBuf: グラフ画像を返すかどうか
        """
        if base_ch:
            # 基準電極が指定されていたらその電極の拍動周期ごとにピーク抽出する
            result = []
            for divided_data in self.data.from_beat_cycles(peak_index, base_ch):
                peak = detect_peak_neg(divided_data)
                times, remove_ch = remove_undetected_ch_from64ch(self.data, peak)
                grad = Gradient(
                    Solver(times[0], remove_ch, self.electrode.ele_dis, mesh_num)
                )
                buf: io.BytesIO = grad.draw2d(
                    contour, isQuiver, dpi=dpi, cmap=cmap, isBuf=isBuf
                )

                if isBuf:
                    result.append(buf)
                else:
                    result.append(grad)
            if isBuf:
                # list[BytesIO]を渡してもlist[FigImage]にキャストされる
                return VideoMEA(result)
            else:
                return result

        else:
            grads = Gradients(self.data, peak_index, self.electrode.ele_dis, mesh_num)
            buf_list = grads.draw_2d(contour, isQuiver, dpi=dpi, cmap=cmap, isBuf=isBuf)

            if isBuf:
                return VideoMEA(buf_list)
            else:
                return grads.gradients

    def draw_3d(
        self,
        peak_index: Peaks64,
        mesh_num=100,
        xlabel="X (μm)",
        ylabel="Y (μm)",
        clabel="Δt (ms)",
        dpi=300,
        isBuf=False,
    ) -> VideoMEA | Gradients:
        """
        3Dカラーマップ描画
        Args:
            peak_index: ピーク抽出結果
            mesh_num: mesh_num x mesh_numでデータを生成
            xlabel: X軸ラベル
            ylabel: Y軸ラベル
            clabel: カラーバーラベル
            dpi: 解像度
            isBuf: グラフ画像を返すかどうか
        """
        grads = Gradients(self.data, peak_index, self.electrode.ele_dis, mesh_num)
        buf_list = grads.draw_3d(xlabel, ylabel, clabel, dpi, isBuf=isBuf)

        if isBuf:
            return VideoMEA(buf_list)
        else:
            return grads

    def draw_line_conduction(
        self,
        peak_index: Peaks64,
        amc_chs: list[int],
        base_ch: int | None = None,
        isLoop=True,
        dpi=300,
        isBuf=False,
    ) -> VideoMEA | None:
        """
        ライン状心筋細胞ネットワークのカラーマップ描画
        電極番号の配列の順番は経路がつながっている順番になるようにすること
        ----------
        Parameters
            peak_index: ピーク抽出結果
            chs: AMCの電極番号配列
            base_ch: 基準電極
            isLoop: 経路が環状かどうか
            dpi: 解像度
            isBuf: グラフ画像を返すかどうか

        -------

        """
        if base_ch:
            # 基準電極が指定されていたらその電極の拍動周期ごとにピーク抽出する
            if base_ch not in amc_chs:
                raise ValueError("基準電極はAMC内の電極から選択してください")

            result = []
            for divided_data in self.data.from_beat_cycles(peak_index, base_ch):
                peak = detect_peak_neg(divided_data)
                times, remove_ch_index = remove_undetected_ch(
                    divided_data, peak, amc_chs
                )
                result.append(
                    draw_line(
                        times[0],
                        amc_chs,
                        remove_ch_index,
                        self.electrode,
                        isLoop,
                        dpi,
                        isBuf=isBuf,
                    )
                )
            if isBuf:
                return VideoMEA(result)
        else:
            buf_list = draw_line_conduction(
                self.data, self.electrode, peak_index, amc_chs, isLoop, dpi, isBuf=isBuf
            )

            if isBuf:
                return VideoMEA(buf_list)
