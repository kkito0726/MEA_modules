import unittest
from test.fixtures import fixture_hed_path
from test.utils import get_resource_path

import pandas as pd

from pyMEA import detect_peak_all, detect_peak_neg, read_MEA
from pyMEA.domain.service.peak_detection import detect_peak_pos


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = fixture_hed_path("cardio")
        self.expect_neg_peak_index_path = get_resource_path(
            "expects/neg_peak_index.csv"
        )
        self.expect_pos_peak_index_path = get_resource_path(
            "expects/pos_peak_index.csv"
        )
        self.expect_all_peak_index_path = get_resource_path(
            "expects/all_peak_index.csv"
        )
        self.mea = read_MEA(self.path.__str__(), 0, 3, 450)
        self.neg_peak_index = detect_peak_neg(self.mea.data)
        self.pos_peak_index = detect_peak_pos(self.mea.data, threshold=2)
        self.all_peak_index = detect_peak_all(self.mea.data, threshold=(2, 2))

    def test_下方向のピークを抽出できる(self):
        expects = pd.read_csv(self.expect_neg_peak_index_path)
        for ch in range(1, 65):
            self.assertEqual(len(self.neg_peak_index[ch]), expects[str(ch)].count())
            for i, index in enumerate(self.neg_peak_index[ch]):
                # OS/数値ライブラリ差でピーク位置が数フレームずれ得るため許容
                self.assertLessEqual(abs(int(expects[str(ch)][i]) - int(index)), 5)
            for value in self.mea.data[ch][self.neg_peak_index[ch]]:
                self.assertTrue(value < -200)

    def test_上方向のピークを抽出できる(self):
        expects = pd.read_csv(self.expect_pos_peak_index_path)
        for ch in range(1, 65):
            self.assertEqual(len(self.pos_peak_index[ch]), expects[str(ch)].count())
            for i, index in enumerate(self.pos_peak_index[ch]):
                self.assertLessEqual(abs(int(expects[str(ch)][i]) - int(index)), 5)
            for value in self.mea.data[ch][self.pos_peak_index[ch]]:
                self.assertTrue(value > 50)

    def test_上下両方向のピークを抽出できる(self):
        expects = pd.read_csv(self.expect_all_peak_index_path)
        for ch in range(1, 65):
            self.assertEqual(len(self.all_peak_index[ch]), expects[str(ch)].count())
            for i, index in enumerate(self.all_peak_index[ch]):
                self.assertLessEqual(abs(int(expects[str(ch)][i]) - int(index)), 5)


if __name__ == "__main__":
    unittest.main()
