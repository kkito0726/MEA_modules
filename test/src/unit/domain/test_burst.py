import unittest
from test.utils import get_resource_path

import numpy as np

from pyMEA import detect_peak_neg, read_MEA
from pyMEA.domain.service.burst import peak_flatten, sbf_detection, sbf_single


class TestBurst(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = get_resource_path("230615_day2_test_5s_.hed")
        cls.mea = read_MEA(path.__str__(), 1, 2, 450)
        cls.peak_index = detect_peak_neg(cls.mea.data)

    def test_全電極のピーク時刻を一次元配列にまとめられる(self):
        flat = peak_flatten(self.mea.data, self.peak_index)

        total_peaks = sum(len(self.peak_index[ch]) for ch in range(1, 65))
        self.assertEqual(total_peaks, len(flat))
        self.assertIsInstance(flat, np.ndarray)
        # 全て読み込み時間の範囲内
        self.assertTrue((flat >= 1).all())
        self.assertTrue((flat <= 2).all())

    def test_同期バースト発火検出が実行できる(self):
        result = sbf_detection(self.mea.data, self.peak_index)
        self.assertIsInstance(result, list)

    def test_1電極バースト発火検出が実行できる(self):
        result = sbf_single(self.mea.data, self.peak_index, ch=32)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
