import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from pyMEA import detect_peak_neg
from pyMEA.calculator.calculator import Calculator
from pyMEA.MEA import MEA

path = "./public/230615_day2_test_5s_.hed"
data = MEA(path, 0, 5)
peak_index = detect_peak_neg(data.array)
calc450 = Calculator(data, 450)
calc150 = Calculator(data, 150)


class CalculatorTest(unittest.TestCase):
    def test_ISIが正しく計算できる(self):
        isi = calc450.isi(peak_index, 32)
        estimate = [0.609, 0.6078, 0.6118, 0.6035, 0.6007, 0.5868, 0.6225]

        for i in range(len(isi)):
            self.assertEqual(isi[i], estimate[i])

    def test_FPDが正しく計算できる(self):
        fpd = calc450.fpd(peak_index, 19)
        estimate = [0.1795, 0.177, 0.1729, 0.1813, 0.1782, 0.1799, 0.1834, 0.1809]

        for i in range(len(fpd)):
            self.assertEqual(round(fpd[i], 2), round(estimate[i], 2))

    def test_電極間距離が正しく計算できる(self):
        self.assertEqual(calc450.distance(1, 2), 450)
        self.assertEqual(calc450.distance(1, 10), 450 * np.sqrt(2))
        self.assertEqual(
            calc450.distance(13, 55), np.sqrt((450 * 2) ** 2 + (450 * 5) ** 2)
        )
        self.assertEqual(
            calc450.distance(8, 57), np.sqrt((450 * 7) ** 2 + (450 * 7) ** 2)
        )

        self.assertEqual(calc150.distance(1, 2), 150)
        self.assertEqual(calc150.distance(1, 10), 150 * np.sqrt(2))
        self.assertEqual(
            calc150.distance(13, 55), np.sqrt((150 * 2) ** 2 + (150 * 5) ** 2)
        )
        self.assertEqual(
            calc150.distance(8, 57), np.sqrt((150 * 7) ** 2 + (150 * 7) ** 2)
        )

    def test_伝導速度が正しく計算できる(self):
        cv = calc450.conduction_velocity(peak_index, 1, 2)
        estimate = [0.23684211, 0.25, 0.225, 0.25, 0.25, 0.25, 0.26470588, 0.26470588]

        for i in range(len(cv)):
            self.assertEqual(round(cv[i], 3), round(estimate[i], 3))

    @patch("matplotlib.pyplot.show")
    def test_速度ベクトルから伝導速度が正しく計算できる(self, mock_show: MagicMock):
        popts, r2s = data.draw_2d(peak_index, 450)
        cvs = calc450.gradient_velocity(popts)

        for cv in cvs:
            self.assertEqual(cv.shape, (64,))
            for c in cv:
                self.assertTrue(0 <= c <= 0.4)

        self.assertEqual(mock_show.call_count, 8)

    def test_電極番号を1から64の範囲外を指定するとき例外が発生する(self):
        with self.assertRaises(ValueError) as context:
            calc450.isi(peak_index, 65)
        self.assertEqual(str(context.exception), "chは1-64の整数で入力してください")

        with self.assertRaises(ValueError) as context:
            calc450.isi(peak_index, 0)
        self.assertEqual(str(context.exception), "chは1-64の整数で入力してください")

        with self.assertRaises(ValueError) as context:
            calc450.isi(peak_index, -1)
        self.assertEqual(str(context.exception), "chは1-64の整数で入力してください")


if __name__ == "__main__":
    unittest.main()
