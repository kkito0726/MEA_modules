from typing import Any

import numpy as np
from numpy import dtype, floating, ndarray

from pyMEA.find_peaks.peak_detection import detect_peak_pos
from pyMEA.find_peaks.peak_model import NegPeaks, Peaks
from pyMEA.fit_gradient import get_mesh, model
from pyMEA.gradient.Gradients import Gradients
from pyMEA.read.MEA import MEA
from pyMEA.utils.decorators import ch_validator


class Calculator:
    def __init__(self, data: MEA, ele_dis: int):
        """
        ISI, FPD, Conduction Velocityを計算するクラス
        ----------
        Args:
            data: MEAデータ (MEAクラスのインスタンス)
            ele_dis: 電極間距離 (μm)
        """
        self.__data = data
        self.ele_dis = ele_dis

    @ch_validator
    def isi(self, peak_index: Peaks, ch) -> ndarray[Any, dtype[floating[Any]]]:
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
        return np.diff(peak_index[ch]) / self.data.SAMPLING_RATE

    @ch_validator
    def fpd(
        self, neg_peak_index: NegPeaks, ch: int, peak_range=(30, 110)
    ) -> ndarray[float, dtype[float]]:
        """
        FPD (s) 細胞外電位継続時間を計算する
        ----------
        Args:
            neg_peak_index: 1stピークの抽出結果
            ch: 電極番号
            peak_range: 2ndピークの電位範囲

        Returns:
           float: FPD (s)
        -------

        """
        # 1st peak付近のデータを0に変換
        for p in neg_peak_index[ch]:
            self.data[ch][p - 200 : p + 200] = 0

        # 各拍動周期で2nd peakを抽出
        fpds = []
        for p in neg_peak_index[ch]:
            tmp = self.data[:, p + 200 : p + 5000]  # 2nd peak付近のデータを抽出
            pos_peak = detect_peak_pos(tmp, height=peak_range, distance=3000)
            # ピークが見つからなかったら飛ばして次の拍動周期
            if len(pos_peak[ch]) == 0:
                continue

            pos_time = tmp[0][pos_peak[ch]]
            fpd = pos_time[0] - self.data[0][p]
            if 0.1 < fpd < 0.4:
                fpds.append(fpd)
            # 範囲外FPDの場合スルー
            else:
                continue

        return np.array(fpds)

    @ch_validator
    def conduction_velocity(self, peak_index: Peaks, ch1: int, ch2: int) -> ndarray:
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

    def gradient_velocity(self, peak_index: Peaks, mesh_num=8):
        """
        速度ベクトルから計算した伝導速度 (m/s)を計算する
        ----------
        Args:
            peak_index: ピーク抽出結果
            mesh_num: 何x何で計算するか

        Returns:
            ndarray: 速度ベクトルから計算した伝導速度 (m/s)
        -------

        """
        grads = Gradients(self.data, peak_index, self.ele_dis, mesh_num)
        return np.array(grads.calc_velocity())

    @property
    def data(self):
        return self.__data

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
