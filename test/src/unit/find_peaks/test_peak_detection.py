import unittest
from test.utils import get_resource_path

import pandas as pd

from pyMEA import detect_peak_all, detect_peak_neg, read_MEA
from pyMEA.find_peaks.peak_detection import detect_peak_pos


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")
        self.expect_neg_peak_index_path = get_resource_path(
            "expects/neg_peak_index.csv"
        )
        self.expect_pos_peak_index_path = get_resource_path(
            "expects/pos_peak_index.csv"
        )
        self.expect_all_peak_index_path = get_resource_path(
            "expects/all_peak_index.csv"
        )
        self.mea = read_MEA(self.path.__str__(), 0, 5, 450)
        self.neg_peak_index = detect_peak_neg(self.mea.data)
        self.pos_peak_index = detect_peak_pos(self.mea.data, threshold=2)
        self.all_peak_index = detect_peak_all(self.mea.data, threshold=(2, 1))

    def test_下方向のピークを抽出できる(self):
        expects = pd.read_csv(self.expect_neg_peak_index_path)
        for ch in range(1, 65):
            for i, index in enumerate(self.neg_peak_index[ch]):
                self.assertEqual(expects[str(ch)][i], index)
            for value in self.mea.data[ch][self.neg_peak_index[ch]]:
                self.assertTrue(value < -200)

    def test_上方向のピークを抽出できる(self):
        expects = pd.read_csv(self.expect_pos_peak_index_path)
        for ch in range(1, 65):
            for i, index in enumerate(self.pos_peak_index[ch]):
                self.assertEqual(expects[str(ch)][i], index)
            for value in self.mea.data[ch][self.pos_peak_index[ch]]:
                self.assertTrue(value > 50)

    def test_上下両方向のピークを抽出できる(self):
        expects = pd.read_csv(self.expect_all_peak_index_path)
        for ch in range(1, 65):
            for i, index in enumerate(self.all_peak_index[ch]):
                self.assertEqual(expects[str(ch)][i], index)


if __name__ == "__main__":
    unittest.main()
