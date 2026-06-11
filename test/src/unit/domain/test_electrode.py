import unittest

import numpy as np

from pyMEA.domain.model.Electrode import Electrode, get_mesh


class TestGetMesh(unittest.TestCase):
    def test_メッシュの形状が指定どおりになる(self):
        for mesh_num in (8, 100):
            xx, yy = get_mesh(450, mesh_num)
            self.assertEqual((mesh_num, mesh_num), xx.shape)
            self.assertEqual((mesh_num, mesh_num), yy.shape)

    def test_メッシュの範囲が電極エリア全体になる(self):
        ele_dis = 450
        xx, yy = get_mesh(ele_dis, 8)
        self.assertEqual(0, xx.min())
        self.assertEqual(ele_dis * 7, xx.max())
        self.assertEqual(0, yy.min())
        self.assertEqual(ele_dis * 7, yy.max())

    def test_y座標は電極番号順に上から下へ並ぶ(self):
        ele_dis = 450
        _, yy = get_mesh(ele_dis, 8)
        # 電極1 (左上) のy座標が最大、電極57 (左下) のy座標が0
        self.assertEqual(ele_dis * 7, yy[0][0])
        self.assertEqual(0, yy[7][0])


class TestElectrode(unittest.TestCase):
    def setUp(self):
        self.electrode = Electrode(450)

    def test_電極メッシュは8x8になる(self):
        xx, yy = self.electrode.get_electrode_mesh
        self.assertEqual((8, 8), xx.shape)
        self.assertEqual((8, 8), yy.shape)

    def test_電極座標を取得できる(self):
        # 電極1は左上 (x=0, y=ele_dis*7)
        x, y = self.electrode.get_coordinate(1)
        self.assertEqual(0, x)
        self.assertEqual(450 * 7, y)

        # 電極64は右下 (x=ele_dis*7, y=0)
        x, y = self.electrode.get_coordinate(64)
        self.assertEqual(450 * 7, x)
        self.assertEqual(0, y)

    def test_電極間の座標距離が電極間距離と一致する(self):
        x1, y1 = self.electrode.get_coordinate(1)
        x2, y2 = self.electrode.get_coordinate(2)
        self.assertAlmostEqual(450, np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))

    def test_範囲外の電極番号はValueErrorになる(self):
        with self.assertRaises(ValueError):
            self.electrode.get_coordinate(0)
        with self.assertRaises(ValueError):
            self.electrode.get_coordinate(65)


if __name__ == "__main__":
    unittest.main()
