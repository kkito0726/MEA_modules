import unittest
from test.utils import get_resource_path

import numpy as np

from pyMEA import detect_peak_neg, read_MEA
from pyMEA.domain.service.gradient.Gradient import grad_model, grad_velocity
from pyMEA.domain.service.gradient.Solver import Solver, model
from pyMEA.domain.service.peak_times import remove_undetected_ch_from64ch


class TestSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = get_resource_path("230615_day2_test_5s_.hed")
        cls.mea = read_MEA(path.__str__(), 1, 2, 450)
        peak_index = detect_peak_neg(cls.mea.data)
        cls.times, cls.remove_ch = remove_undetected_ch_from64ch(
            cls.mea.data, peak_index
        )

    def test_フィッティング結果が正しい形状になる(self):
        solver = Solver(self.times[0], self.remove_ch, 450, 100)

        # 3次多項式の係数は10個
        self.assertEqual(10, len(solver.popt))
        # 決定係数が計算されている
        self.assertTrue(0 < solver.r2 <= 1)
        # メッシュはmesh_num x mesh_num
        self.assertEqual((100, 100), solver.xx.shape)
        self.assertEqual((100, 100), solver.yy.shape)
        self.assertEqual(100 * 100, len(solver.z))

    def test_zは発火起点が0msに正規化される(self):
        solver = Solver(self.times[0], self.remove_ch, 450, 50)
        self.assertAlmostEqual(0, solver.z.min())

    def test_solverの配列はイミュータブル(self):
        solver = Solver(self.times[0], self.remove_ch, 450, 50)
        with self.assertRaises(ValueError):
            solver.xx[0][0] = 999

    def test_model式が定数項のみの場合は定数を返す(self):
        xx, yy = np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, 1, 4))
        z = model((xx, yy), 5, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertTrue((z == 5).all())

    def test_grad_modelは線形項の係数を勾配として返す(self):
        xx, yy = np.meshgrid(np.linspace(0, 1, 4), np.linspace(0, 1, 4))
        # z = 2x + 3y -> grad_x = 2, grad_y = 3
        grad_x, grad_y = grad_model((xx, yy), 0, 2, 3, 0, 0, 0, 0, 0, 0, 0)
        self.assertTrue((grad_x == 2).all())
        self.assertTrue((grad_y == 3).all())

    def test_grad_velocityは勾配の逆数方向の速度を返す(self):
        grad_x = np.array([1.0])
        grad_y = np.array([0.0])
        vx, vy = grad_velocity(grad_x, grad_y)
        self.assertAlmostEqual(1.0, vx[0])
        self.assertAlmostEqual(0.0, vy[0])


if __name__ == "__main__":
    unittest.main()
