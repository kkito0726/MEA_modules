import unittest

from pyMEA import detect_peak_neg
from pyMEA.gradient.Gradients import Gradients
from pyMEA.read.MEA import MEA
from test.utils import  get_resource_path


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")

    def test_Gradientsが正しくインスタンス化される(self):
        start, end = 1, 2
        data = MEA(self.path.__str__(), start, end)
        peak_index = detect_peak_neg(data)
        ele_dis = 450

        gradients = Gradients(data, peak_index, ele_dis)

        # 決定係数が計算されている
        for r2 in gradients.r2s:
            self.assertTrue(0 < r2 < 1)

        # 伝導速度が計算されている
        for conduction_velocity in gradients.calc_velocity():
            for cv in conduction_velocity:
                self.assertTrue(0 < cv < 0.5)

        for gradient in gradients:
            self.assertEqual((100, 100), gradient.grad_x.shape)
            self.assertEqual((100, 100), gradient.grad_y.shape)
            self.assertEqual((100, 100), gradient.vx.shape)
            self.assertEqual((100, 100), gradient.vy.shape)


if __name__ == '__main__':
    unittest.main()
