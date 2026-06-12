from dataclasses import dataclass

import numpy as np

from pyMEA.domain.model.Electrode import Electrode
from pyMEA.domain.model.MEA import MEA
from pyMEA.domain.model.peak_model import Peaks64
from pyMEA.domain.service.gradient.Gradient import Gradient
from pyMEA.domain.service.gradient.Gradients import Gradients
from pyMEA.presentation.FigImage import FigImage
from pyMEA.presentation.plot import colormap, waveform
from pyMEA.presentation.plot.color import normalize_color
from pyMEA.presentation.plot.histogram import mkHist
from pyMEA.presentation.plot.plot import showDetection
from pyMEA.presentation.plot.raster_plot import raster_plot
from pyMEA.presentation.video import VideoMEA


@dataclass(frozen=True)
class FigMEA:
    """グラフ描画のファサード。

    各メソッドの実装本体は presentation/plot/ 配下の小モジュールにある。
    """

    data: MEA
    electrode: Electrode

    def _set_times(self, start, end) -> tuple[int, int]:
        # 時間の設定がなければ読み込み時間全体をプロットするようにする。
        if start is None:
            start = self.data.start
        if end is None:
            end = self.data.end

        return start, end

    def plot_spectrum(
        self, ch: int, max_freq=500, nperseg=2048, figsize=(10, 4), dpi=100, isBuf=False
    ):
        """
        与えられた信号のスペクトルをプロットする関数
        - FFTの振幅スペクトル
        """
        return waveform.plot_spectrum(
            self.data,
            ch,
            max_freq=max_freq,
            nperseg=nperseg,
            figsize=figsize,
            dpi=dpi,
            isBuf=isBuf,
        )

    def showAll(
        self,
        start=None,
        end=5,
        volt_min=-200,
        volt_max=200,
        figsize=(8, 8),
        dpi=300,
        color: list[str] | list[list[float]] = None,
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
            color: プロットの配色
            isBuf: グラフ画像を返すかどうか
        """
        return waveform.show_all(
            self.data,
            start=start,
            end=end,
            volt_min=volt_min,
            volt_max=volt_max,
            figsize=figsize,
            dpi=dpi,
            color=color,
            isBuf=isBuf,
        )

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
        color: str = None,
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
            color: プロットの配色
            isBuf: グラフ画像を返すかどうか
        """
        start, end = self._set_times(start, end)
        return waveform.show_single(
            self.data,
            ch,
            start,
            end,
            volt_min=volt_min,
            volt_max=volt_max,
            figsize=figsize,
            dpi=dpi,
            xlabel=xlabel,
            ylabel=ylabel,
            color=color,
            isBuf=isBuf,
        )

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
        color: str = None,
        peak_color: list[str] | list[list[float]] = None,
        isBuf=False,
    ) -> FigImage | None:
        """
        1電極の波形とピークの位置をプロット

        Args:
            ch: 描画する電極番号
            *peak_indexes: ピーク配列 (可変長)以降の引数は引数名を指定する
            start: 読み込み開始時間 [s]
            end: 読み込み終了時間[s]
            volt_min: マイナス電位 [μV]
            volt_max: プラス電位 [μV]
            figsize: figのアスペクト比
            color: プロットの配色
            peak_color: ピークのプロットの配色
            dpi: 解像度
            xlabel: X軸ラベル
            ylabel: Y軸ラベル
            isBuf: グラフ画像を返すかどうか
        """
        start, end = self._set_times(start, end)
        return waveform.plot_peaks(
            self.data,
            ch,
            *peak_indexes,
            start=start,
            end=end,
            volt_min=volt_min,
            volt_max=volt_max,
            figsize=figsize,
            dpi=dpi,
            xlabel=xlabel,
            ylabel=ylabel,
            color=color,
            peak_color=peak_color,
            isBuf=isBuf,
        )

    def showDetection(
        self,
        eles: list[int],
        start=None,
        end=None,
        adjust_wave=200,
        isDisplayCh=True,
        figsize=(12, 12),
        xlabel="Time (s)",
        ylabel="Electrode Number",
        dpi=300,
        color: list[str] | list[list[float]] = None,
        isBuf=False,
    ) -> FigImage | None:
        """
        波形を縦に積み上げて描画する
        Args:
            eles: 電極番号のリスト
            start: 描画開始時刻 (s)
            end: 描画終了時刻 (s)
            adjust_wave: 波形を何分の一にして描画するか
            isDisplayCh: 電極番号をY軸の目盛りにするか
            figsize: figの縦横比
            xlabel: X軸ラベル
            ylabel: Y軸ラベル
            dpi: 解像度
            color: プロットの配色
            isBuf: 画像のバッファを返すかどうか
        """
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
            isDisplayCh=isDisplayCh,
            figsize=figsize,
            xlabel=xlabel,
            ylabel=ylabel,
            dpi=dpi,
            color=normalize_color(color, None),
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
        return colormap.draw_2d(
            self.data,
            self.electrode,
            peak_index,
            base_ch=base_ch,
            mesh_num=mesh_num,
            contour=contour,
            isQuiver=isQuiver,
            dpi=dpi,
            cmap=cmap,
            isBuf=isBuf,
        )

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
        return colormap.draw_3d(
            self.data,
            self.electrode,
            peak_index,
            mesh_num=mesh_num,
            xlabel=xlabel,
            ylabel=ylabel,
            clabel=clabel,
            dpi=dpi,
            isBuf=isBuf,
        )

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
            amc_chs: AMCの電極番号配列
            base_ch: 基準電極
            isLoop: 経路が環状かどうか
            dpi: 解像度
            isBuf: グラフ画像を返すかどうか

        -------

        """
        return colormap.draw_line_conduction_map(
            self.data,
            self.electrode,
            peak_index,
            amc_chs,
            base_ch=base_ch,
            isLoop=isLoop,
            dpi=dpi,
            isBuf=isBuf,
        )
