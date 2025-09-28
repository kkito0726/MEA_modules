from dataclasses import dataclass

import numpy as np
from numpy import ndarray

from pyMEA.calculator.values.FPD import FPD
from pyMEA.calculator.values.ISI import ISI
from pyMEA.find_peaks.peak_detection import detect_cardio_second_peak, detect_peak_neg
from pyMEA.find_peaks.peak_model import NegPeaks64, Peaks64, PosPeaks
from pyMEA.gradient.Gradient import Gradient
from pyMEA.gradient.Gradients import Gradients
from pyMEA.read.model.MEA import MEA
from pyMEA.utils.decorators import ch_validator


@dataclass(frozen=True)
class Calculator:
    """
    ISI, FPD, Conduction Velocityを計算するクラス
    ----------
    Args:
        data: MEAデータ (MEAクラスのインスタンス)
        ele_dis: 電極間距離 (μm)
    """

    data: MEA
    ele_dis: int

    @ch_validator
    def isi(self, peak_index: Peaks64, ch) -> ISI:
        """
        ISI (s) 拍動間隔を計算する
        ----------
        Args:
            peak_index: ピーク抽出結果
            ch: 電極番号

        Returns:
            float: ISI (s)
        -------

        """

        return ISI(
            values=np.diff(peak_index[ch]) / self.data.SAMPLING_RATE,
            ch=ch,
            data=self.data,
            peaks=peak_index[ch]
        )

    @ch_validator
    def fpd(
        self,
        neg_peak_index: NegPeaks64,
        ch: int,
        peak_range=(30, 110),
        stroke_time=0.02,
        fpd_range=(0.1, 0.4),
        prominence=None,
        width=None,
    ) -> FPD:
        """
        FPD (s) 細胞外電位継続時間を計算する
        ----------
        Args:
            neg_peak_index: 1stピークの抽出結果
            ch: 電極番号
            peak_range: 2ndピークの電位範囲
            stroke_time: ピークに達するまでの時間 (s)
            fpd_range: 許容するFPDの範囲
            prominence: 突起度
            width: ピークの幅

        Returns:
            FPD
        -------

        Parameters
        ----------
        """
        stroke_frame = int(stroke_time * self.data.SAMPLING_RATE)
        data = self.data.array.copy()
        # 1st peak付近のデータを0に変換
        for p in neg_peak_index[ch]:
            data[ch][p - stroke_frame : p + stroke_frame] = 0

        fpds = []
        pos_peaks = []
        max_fpd_frame = int(0.5 * self.data.SAMPLING_RATE)
        # 各拍動周期で2nd peakを抽出
        for p in neg_peak_index[ch]:
            tmp = data[:, p + stroke_frame : p + max_fpd_frame]
            # 2nd peak付近のデータを抽出
            pos_peak = detect_cardio_second_peak(
                tmp,
                height=peak_range,
                distance=3000,
                width=width,
                prominence=prominence,
            )
            # ピークが見つからなかったら飛ばして次の拍動周期
            if len(pos_peak[ch]) == 0:
                continue

            pos_time = tmp[0][pos_peak[ch]]
            fpd = pos_time[0] - data[0][p]
            if fpd_range[0] < fpd < fpd_range[1]:
                fpds.append(fpd)
                pos_peaks.append(p + stroke_frame + pos_peak[ch][0])
            # 範囲外FPDの場合スルー
            else:
                continue
        return FPD(
            values=np.array(fpds),
            ch=ch,
            data=self.data,
            neg_peaks=neg_peak_index[ch],
            pos_peaks=PosPeaks(np.array(pos_peaks)),
        )

    @ch_validator
    def conduction_velocity(self, peak_index: Peaks64, ch1: int, ch2: int) -> ndarray:
        """
        伝導速度 (m/s)を計算する
        ----------
        Args:
            peak_index: ピーク抽出結果
            ch1: 電極番号1
            ch2: 電極番号2

        Returns:
            float: 伝導速度 (s)
        -------

        """
        if len(peak_index[ch1]) != len(peak_index[ch2]):
            raise ValueError("ピーク抽出数が2電極間で一致しません")

        conduction_time = (
            abs(peak_index[ch1] - peak_index[ch2]) / self.data.SAMPLING_RATE
        )
        distance = self.distance(ch1, ch2) * 10**-6
        return distance / conduction_time

    @ch_validator
    def distance(self, ch1: int, ch2: int) -> np.float64:
        """
        指定した電極間距離 (μm)を計算する
        ----------
        Args:
            ch1: 電極番号1
            ch2: 電極番号2

        Returns:
            float: 電極間距離 (μm)
        -------
        """
        ele_dict = self.__ele_dict()
        return np.sqrt(
            (ele_dict[ch1][0] - ele_dict[ch2][0]) ** 2
            + (ele_dict[ch1][1] - ele_dict[ch2][1]) ** 2
        )

    def gradient_velocity(self, peak_index: Peaks64, base_ch=None, mesh_num=8):
        """
        速度ベクトルから計算した伝導速度 (m/s)を計算する
        ----------
        Args:
            peak_index: ピーク抽出結果
            base_ch: 基準電極
            mesh_num: 何x何で計算するか

        Returns:
            ndarray: 速度ベクトルから計算した伝導速度 (m/s)
        -------

        """
        if base_ch:
            # 基準電極が指定されていたらその電極の拍動周期ごとにピーク抽出する
            results: list[Gradient] = []
            for divided_data in self.data.from_beat_cycles(peak_index, base_ch):
                peak = detect_peak_neg(divided_data)
                grads = Gradients(self.data, peak, self.ele_dis, mesh_num)
                results.append(*grads.gradients)
            return np.array([result.calc_velocity() for result in results])
        else:
            grads = Gradients(self.data, peak_index, self.ele_dis, mesh_num)
            return np.array(grads.calc_velocity())

    def __ele_dict(self) -> dict[int, tuple[int, ...]]:
        ele_dict = {}
        for i, dis in enumerate(base_ele_point):
            ele_dict[i + 1] = dis * self.ele_dis
        return ele_dict


base_ele_point = np.array(
    [
        [0.0, 7.0],
        [1.0, 7.0],
        [2.0, 7.0],
        [3.0, 7.0],
        [4.0, 7.0],
        [5.0, 7.0],
        [6.0, 7.0],
        [7.0, 7.0],
        [0.0, 6.0],
        [1.0, 6.0],
        [2.0, 6.0],
        [3.0, 6.0],
        [4.0, 6.0],
        [5.0, 6.0],
        [6.0, 6.0],
        [7.0, 6.0],
        [0.0, 5.0],
        [1.0, 5.0],
        [2.0, 5.0],
        [3.0, 5.0],
        [4.0, 5.0],
        [5.0, 5.0],
        [6.0, 5.0],
        [7.0, 5.0],
        [0.0, 4.0],
        [1.0, 4.0],
        [2.0, 4.0],
        [3.0, 4.0],
        [4.0, 4.0],
        [5.0, 4.0],
        [6.0, 4.0],
        [7.0, 4.0],
        [0.0, 3.0],
        [1.0, 3.0],
        [2.0, 3.0],
        [3.0, 3.0],
        [4.0, 3.0],
        [5.0, 3.0],
        [6.0, 3.0],
        [7.0, 3.0],
        [0.0, 2.0],
        [1.0, 2.0],
        [2.0, 2.0],
        [3.0, 2.0],
        [4.0, 2.0],
        [5.0, 2.0],
        [6.0, 2.0],
        [7.0, 2.0],
        [0.0, 1.0],
        [1.0, 1.0],
        [2.0, 1.0],
        [3.0, 1.0],
        [4.0, 1.0],
        [5.0, 1.0],
        [6.0, 1.0],
        [7.0, 1.0],
        [0.0, 0.0],
        [1.0, 0.0],
        [2.0, 0.0],
        [3.0, 0.0],
        [4.0, 0.0],
        [5.0, 0.0],
        [6.0, 0.0],
        [7.0, 0.0],
    ]
)
