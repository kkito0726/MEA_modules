from dataclasses import dataclass
from functools import cached_property

import numpy as np
from numpy import float64
from numpy._typing import NDArray

from pyMEA.utils.decorators import ch_validator


@dataclass(frozen=True)
class Electrode:
    ele_dis: int

    @cached_property
    def get_mesh(self) -> tuple[NDArray[float64], NDArray[float64]]:
        """
        グリッド配列を取得するメソッド
        """
        # データ範囲を取得
        x_min, x_max = 0, self.ele_dis * 7
        y_min, y_max = 0, self.ele_dis * 7

        # 取得したデータ範囲で新しく座標にする配列を作成
        x_coord = np.linspace(x_min, x_max, 8)
        y_coord = np.linspace(y_min, y_max, 8)

        # 取得したデータ範囲で新しく座標にする配列を作成
        xx, yy = np.meshgrid(x_coord, y_coord)

        # 電極番号順に配列を修正
        yy = np.rot90(np.rot90(yy))

        return xx, yy

    @ch_validator
    def get_coordinate(self, ch: int) -> tuple[NDArray[float64], NDArray[float64]]:
        mesh = self.get_mesh
        x = mesh[0][(ch - 1) // 8][(ch - 1) % 8]
        y = mesh[1][(ch - 1) // 8][(ch - 1) % 8]
        return x, y
