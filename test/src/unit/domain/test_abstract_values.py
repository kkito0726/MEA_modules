import unittest

import numpy as np

from pyMEA.domain.value.AbstractValues import AbstractValues


class TestAbstractValues(unittest.TestCase):
    def setUp(self):
        self.values = AbstractValues(np.array([1.0, 2.0, 3.0, 4.0]))

    def test_統計量を計算できる(self):
        self.assertAlmostEqual(2.5, self.values.mean)
        self.assertAlmostEqual(np.std([1, 2, 3, 4]), self.values.std)
        self.assertAlmostEqual(self.values.std / 4, self.values.se)
        # STV: 連続差分の絶対値の合計 / (N * sqrt(2))
        self.assertAlmostEqual(3 / (3 * np.sqrt(2)), self.values.stv)
        self.assertAlmostEqual(
            np.std([1, 2, 3, 4]) / 2.5 * 100, self.values.coefficient_of_variation
        )

    def test_算術演算はndarrayに委譲される(self):
        np.testing.assert_array_equal(np.array([2.0, 3.0, 4.0, 5.0]), self.values + 1)
        np.testing.assert_array_equal(np.array([0.0, 1.0, 2.0, 3.0]), self.values - 1)
        np.testing.assert_array_equal(np.array([2.0, 4.0, 6.0, 8.0]), self.values * 2)
        np.testing.assert_array_equal(np.array([0.5, 1.0, 1.5, 2.0]), self.values / 2)
        np.testing.assert_array_equal(np.array([0.0, 1.0, 1.0, 2.0]), self.values // 2)

    def test_比較演算ができる(self):
        np.testing.assert_array_equal([False, False, True, True], self.values > 2)
        np.testing.assert_array_equal([True, True, False, False], self.values <= 2)
        self.assertEqual(self.values, AbstractValues(np.array([1.0, 2.0, 3.0, 4.0])))
        # AbstractValues以外との __eq__ はFalseになる (__ne__は要素ごとの配列を返す仕様)
        self.assertFalse(self.values == "not values")

    def test_インデックスアクセスと長さを取得できる(self):
        self.assertEqual(4, len(self.values))
        self.assertEqual(3.0, self.values[2])


if __name__ == "__main__":
    unittest.main()
