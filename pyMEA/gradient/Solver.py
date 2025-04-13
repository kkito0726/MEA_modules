from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Union

import numpy as np
from numpy import float64
from numpy._typing import NDArray
from scipy.optimize import curve_fit


@dataclass(frozen=True)
class Solver:
    """
    Args:
        time: 波形のピーク時刻
        remove_ch: ピーク抽出できなかった電極
        ele_dis: 電極間距離
        mesh_num: 何x何のグリッドでデータを補間するか
    """

    time: list[float64]
    remove_ch: list[int]
    ele_dis: int
    mesh_num: int = 100
    popt: NDArray[float64] = field(init=False)
    r2: Union[int, Any] = field(init=False)
    xx: NDArray[float64] = field(init=False)
    yy: NDArray[float64] = field(init=False)

    def __post_init__(self):
        popt, r2 = self.fit_data()
        xx, yy = get_mesh(self.ele_dis, self.mesh_num)
        object.__setattr__(self, "popt", self.freeze_array(popt))
        object.__setattr__(self, "r2", r2)
        object.__setattr__(self, "xx", self.freeze_array(xx))
        object.__setattr__(self, "yy", self.freeze_array(yy))

    @staticmethod
    def freeze_array(arr: NDArray[Any]) -> NDArray[Any]:
        arr.setflags(write=False)
        return arr

    @cached_property
    def z(self) -> NDArray[float64]:
        z = model((self.xx, self.yy), *self.popt)
        z -= np.min(z)  # 発火起点を0 sとする
        z *= 1000  # 単位をmsに変更

        return z

    def fit_data(self) -> tuple[NDArray[float64], Union[int, Any]]:
        """
        MEAの計測データからmodel式にデータをフィッティングする

        Returns:
            popt: モデル式の係数が入ったリスト
            r2: 決定係数
        """
        xx, yy = get_mesh(self.ele_dis, 8)
        xx = np.delete(xx, self.remove_ch)
        yy = np.delete(yy, self.remove_ch)

        popt, _ = curve_fit(model, [xx, yy], self.time)

        residuals = self.time - model([xx, yy], *popt)
        rss = np.sum(residuals**2)
        tss = np.sum((self.time - np.mean(self.time)) ** 2)
        r2 = 1 - (rss / tss)

        return np.array(popt), r2


def get_mesh(ele_dis: int, mesh_num: int) -> tuple[NDArray[float64], NDArray[float64]]:
    """
    グリッド配列を取得するメソッド
    """
    # データ範囲を取得
    x_min, x_max = 0, ele_dis * 7
    y_min, y_max = 0, ele_dis * 7

    # 取得したデータ範囲で新しく座標にする配列を作成
    x_coord = np.linspace(x_min, x_max, mesh_num)
    y_coord = np.linspace(y_min, y_max, mesh_num)

    # 取得したデータ範囲で新しく座標にする配列を作成
    xx, yy = np.meshgrid(x_coord, y_coord)

    # 電極番号順に配列を修正
    yy = np.rot90(np.rot90(yy))

    return xx, yy


def model(
    X: tuple[NDArray[float64], NDArray[float64]],
    p00,
    p10,
    p01,
    p20,
    p11,
    p02,
    p30,
    p21,
    p12,
    p03,
) -> NDArray[float64]:
    x, y = X
    z = (
        p00
        + p10 * x
        + p01 * y
        + p20 * x**2
        + p11 * x * y
        + p02 * y**2
        + p30 * x**3
        + p21 * x**2 * y
        + p12 * x * y**2
        + p03 * y**3
    )
    return z.ravel()
