from dataclasses import dataclass
from functools import cached_property

import numpy as np
from numpy import float64
from numpy._typing import NDArray

from pyMEA.constants import ELECTRODE_GRID_SIZE
from pyMEA.domain.validators import ch_validator


def get_mesh(
    ele_dis: int, mesh_num: int
) -> tuple[NDArray[float64], NDArray[float64]]:
    """
    電極エリアを mesh_num x mesh_num に分割したグリッド配列を取得する
    """
    # データ範囲を取得
    x_min, x_max = 0, ele_dis * (ELECTRODE_GRID_SIZE - 1)
    y_min, y_max = 0, ele_dis * (ELECTRODE_GRID_SIZE - 1)

    # 取得したデータ範囲で新しく座標にする配列を作成
    x_coord = np.linspace(x_min, x_max, mesh_num)
    y_coord = np.linspace(y_min, y_max, mesh_num)

    # 取得したデータ範囲で新しく座標にする配列を作成
    xx, yy = np.meshgrid(x_coord, y_coord)

    # 電極番号順に配列を修正
    yy = np.rot90(np.rot90(yy))

    return xx, yy


@dataclass(frozen=True)
class Electrode:
    ele_dis: int

    @cached_property
    def get_electrode_mesh(self) -> tuple[NDArray[float64], NDArray[float64]]:
        """
        電極のグリッド配列 (8 x 8)を取得するメソッド
        """
        return get_mesh(self.ele_dis, ELECTRODE_GRID_SIZE)

    @ch_validator
    def get_coordinate(self, ch: int) -> tuple[NDArray[float64], NDArray[float64]]:
        """
        指定した電極の座標を取得するメソッド
        Parameters
        ----------
        ch: 電極番号

        Returns
        -------

        """
        mesh = self.get_electrode_mesh
        x = mesh[0][(ch - 1) // ELECTRODE_GRID_SIZE][(ch - 1) % ELECTRODE_GRID_SIZE]
        y = mesh[1][(ch - 1) // ELECTRODE_GRID_SIZE][(ch - 1) % ELECTRODE_GRID_SIZE]
        return x, y
