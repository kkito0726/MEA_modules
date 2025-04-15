import unittest
from test.src.unit.test_utils.utils import truncate
from test.utils import get_resource_path

import numpy as np
import pandas as pd

from pyMEA import detect_peak_neg
from pyMEA.calculator.calculator import Calculator
from pyMEA.figure.FigMEA import FigMEA
from pyMEA.read.model.MEA import MEA


class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")
        self.expect_gradient_velocity_path = get_resource_path(
            "expects/gradient_velocity.csv"
        )
        self.data = MEA(self.path.__str__(), 0, 5)
        self.peak_index = detect_peak_neg(self.data)
        self.calc450 = Calculator(self.data, 450)
        self.calc150 = Calculator(self.data, 150)
        self.fm = FigMEA(self.data)

    def test_ISIが正しく計算できる(self):
        isi = self.calc450.isi(self.peak_index, 32)
        estimate = [0.609, 0.6078, 0.6118, 0.6035, 0.6007, 0.5868, 0.6225]

        for i in range(len(isi)):
            self.assertEqual(isi[i], estimate[i])

    def test_FPDが正しく計算できる(self):
        fpd = self.calc450.fpd(self.peak_index, 19)
        estimate = [0.1795, 0.177, 0.1729, 0.1813, 0.1782, 0.1799, 0.1834, 0.1809]

        for i in range(len(fpd)):
            self.assertEqual(round(fpd[i], 2), round(estimate[i], 2))

    def test_電極間距離が正しく計算できる(self):
        self.assertEqual(self.calc450.distance(1, 2), 450)
        self.assertEqual(self.calc450.distance(1, 10), 450 * np.sqrt(2))
        self.assertEqual(
            self.calc450.distance(13, 55), np.sqrt((450 * 2) ** 2 + (450 * 5) ** 2)
        )
        self.assertEqual(
            self.calc450.distance(8, 57), np.sqrt((450 * 7) ** 2 + (450 * 7) ** 2)
        )

        self.assertEqual(self.calc150.distance(1, 2), 150)
        self.assertEqual(self.calc150.distance(1, 10), 150 * np.sqrt(2))
        self.assertEqual(
            self.calc150.distance(13, 55), np.sqrt((150 * 2) ** 2 + (150 * 5) ** 2)
        )
        self.assertEqual(
            self.calc150.distance(8, 57), np.sqrt((150 * 7) ** 2 + (150 * 7) ** 2)
        )

    def test_伝導速度が正しく計算できる(self):
        cv = self.calc450.conduction_velocity(self.peak_index, 1, 2)
        estimate = [0.23684211, 0.25, 0.225, 0.25, 0.25, 0.25, 0.26470588, 0.26470588]

        for i in range(len(cv)):
            self.assertEqual(round(cv[i], 3), round(estimate[i], 3))

    def test_速度ベクトルから伝導速度が正しく計算できる(self):
        cvs = self.calc450.gradient_velocity(self.peak_index)
        expects = pd.read_csv(self.expect_gradient_velocity_path)

        for i, cv in enumerate(cvs):
            self.assertEqual(cv.shape, (64,))
            for j, c in enumerate(cv):
                self.assertEqual(truncate(expects[str(i)][j], 10), truncate(c, 10))

    def test_電極番号を1から64の範囲外を指定するとき例外が発生する(self):
        with self.assertRaises(ValueError) as context:
            self.calc450.isi(self.peak_index, 65)
        self.assertEqual(str(context.exception), "chは1-64の整数で入力してください")

        with self.assertRaises(ValueError) as context:
            self.calc450.isi(self.peak_index, 0)
        self.assertEqual(str(context.exception), "chは1-64の整数で入力してください")

        with self.assertRaises(ValueError) as context:
            self.calc450.isi(self.peak_index, -1)
        self.assertEqual(str(context.exception), "chは1-64の整数で入力してください")


if __name__ == "__main__":
    unittest.main()
