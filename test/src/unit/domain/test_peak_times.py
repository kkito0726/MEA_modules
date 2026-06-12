import unittest
from test.fixtures import fixture_hed_path

from pyMEA import detect_peak_neg, read_MEA
from pyMEA.domain.service.peak_times import (
    remove_undetected_ch,
    remove_undetected_ch_from64ch,
)


class TestPeakTimes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = fixture_hed_path("cardio")
        cls.mea = read_MEA(path.__str__(), 1, 2, 450)
        cls.peak_index = detect_peak_neg(cls.mea.data)

    def test_64電極のピーク時刻行列を取得できる(self):
        times, remove_ch = remove_undetected_ch_from64ch(self.mea.data, self.peak_index)

        # 残った電極数 + 除去電極数 = 64
        self.assertEqual(64, times.shape[1] + len(remove_ch))
        # ピーク時刻は読み込み時間の範囲内
        self.assertTrue((times >= 1).all())
        self.assertTrue((times <= 2).all())

    def test_指定電極のみのピーク時刻行列を取得できる(self):
        chs = [31, 32, 33, 34]
        times, remove_ch_index = remove_undetected_ch(self.mea.data, self.peak_index, chs)

        self.assertEqual(len(chs), times.shape[1] + len(remove_ch_index))
        # 除去インデックスはchsのインデックス範囲内
        for i in remove_ch_index:
            self.assertTrue(0 <= i < len(chs))

    def test_64電極版は汎用版と同じ結果を返す(self):
        times64, remove64 = remove_undetected_ch_from64ch(self.mea.data, self.peak_index)
        times, remove = remove_undetected_ch(
            self.mea.data, self.peak_index, list(range(1, 65))
        )

        self.assertEqual(remove64, remove)
        self.assertTrue((times64 == times).all())


if __name__ == "__main__":
    unittest.main()
