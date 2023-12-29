import numpy as np
import matplotlib.pyplot as plt

from pyMEA.read_bio import decode_hed, hed2array
from pyMEA.plot import showDetection
from pyMEA.fit_gradient import remove_fit_data, draw_2d, draw_3d
from numpy import ndarray


class MEA:
    def __init__(self, hed_path: str, start: int = 0, end: int = 120) -> None:
        self.hed_path: str = hed_path
        self.start: int = start
        self.end: int = end
        self.time: int = end - start
        self.SAMPLING_RATE, self.GAIN = decode_hed(self.hed_path)
        self.array: ndarray = hed2array(self.hed_path, self.start, self.end)

    def __repr__(self) -> ndarray:
        return repr(self.array)

    def __getitem__(self, index: int) -> ndarray:
        return self.array[index]

    def __len__(self) -> int:
        return len(self.array)

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
    def info(self) -> None:
        print(
            f"読み込み開始時間  : {self.start} s\n読み込み終了時間  : {self.end} s\n読み込み合計時間  : {self.time} s\nサンプリングレート: {self.SAMPLING_RATE} Hz\nGAIN           : {self.GAIN}"
        )

    def showAll(
        self, start=None, end=5, volt_min=-200, volt_max=200, figsize=(8, 8), dpi=300
    ) -> None:
        # 時間の設定がない場合はデータの最初から5秒間をプロットする。
        if start == None:
            start = self.start
        if end == None:
            end == start + 5

        # 読み込み開始時間が0ではないときズレが生じるため差を取っている
        start_frame = int(abs(self.start - start) * self.SAMPLING_RATE)
        end_frame = int(abs(self.start - end) * self.SAMPLING_RATE)

        plt.figure(figsize=figsize, dpi=dpi)
        for i in range(1, 65, 1):
            plt.subplot(8, 8, i)
            plt.plot(
                self.array[0][start_frame:end_frame],
                self.array[i][start_frame:end_frame],
            )
            plt.ylim(volt_min, volt_max)

        plt.show()

    def showSingle(
        self,
        ch: int,
        start: int = None,
        end: int = None,
        volt_min=-200,
        volt_max=200,
        figsize=(8, 2),
        dpi=300,
        xlabel="Time (s)",
        ylabel="Voltage (μV)",
    ) -> None:
        # 時間の設定がなければ全体をプロットするようにする。
        if start == None:
            start = self.start
        if end == None:
            end = self.end

        # 読み込み開始時間が0ではないときズレが生じるため差を取っている
        start_frame = int(abs(self.start - start) * self.SAMPLING_RATE)
        end_frame = int(abs(self.start - end) * self.SAMPLING_RATE)

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(
            self.array[0][start_frame:end_frame], self.array[ch][start_frame:end_frame]
        )
        plt.xlim(start, end)
        plt.ylim(volt_min, volt_max)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.show()

    def showDetection(
        self,
        eles: list[int],
        start=None,
        end=None,
        figsize=(12, 12),
        xlabel="Time (s)",
        ylabel="Electrode Number",
        dpi=300,
    ) -> None:
        # 時間の設定がなければ全体をプロットするようにする。
        if start == None:
            start = self.start
        if end == None:
            end = self.end

        # 読み込み開始時間が途中からの場合のズレを解消する
        start = abs(start - self.start)
        end = abs(end - self.start)
        showDetection(
            MEA_raw=self.array,
            eles=eles,
            start=start,
            read_start=self.start,
            end=end,
            sampling_rate=self.SAMPLING_RATE,
            figsize=figsize,
            xlabel=xlabel,
            ylabel=ylabel,
            dpi=dpi,
        )

    def draw_2d(
        self,
        peak_index: ndarray,
        ele_dis=450,  # 電極間距離 (μm)
        mesh_num=100,  # mesh_num x mesh_numでデータを生成
        contour=False,  # 等高線で表示するかどうか
        isQuiver=False,  # 速度ベクトルを表示するかどうか
        dpi=300,
    ) -> tuple[ndarray, ndarray]:
        popts, r2s = remove_fit_data(self.array, peak_index=peak_index, ele_dis=ele_dis)
        draw_2d(
            popts=popts,
            ele_dis=ele_dis,
            mesh_num=mesh_num,
            contour=contour,
            isQuiver=isQuiver,
            dpi=dpi,
        )

        return popts, r2s

    def draw_3d(
        self,
        peak_index: ndarray,
        ele_dis=450,
        mesh_num=100,
        xlabel="X (μm)",
        ylabel="Y (μm)",
        clabel="Δt (ms)",
        dpi=300,
    ) -> tuple[ndarray, ndarray]:
        popts, r2s = remove_fit_data(self.array, peak_index=peak_index, ele_dis=ele_dis)
        draw_3d(
            popts=popts,
            ele_dis=ele_dis,
            mesh_num=mesh_num,
            xlabel=xlabel,
            ylabel=ylabel,
            clabel=clabel,
            dpi=dpi,
        )

        return popts, r2s
