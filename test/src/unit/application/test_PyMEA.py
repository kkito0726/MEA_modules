import unittest
from test.fixtures import fixture_hed_path

import numpy as np

from pyMEA import MutableMEA, detect_peak_neg, read_MEA


class TestPyMEATransformations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = fixture_hed_path("cardio")
        cls.mea = read_MEA(cls.path.__str__(), 0, 3, 450)

    def test_from_sliceで切り出した区間の責務クラスが再構築される(self):
        sliced = self.mea.from_slice(1, 3)

        self.assertEqual(1, sliced.data.start)
        self.assertEqual(3, sliced.data.end)
        # fig, calculatorが新しいdataを参照している
        self.assertIs(sliced.data, sliced.fig.data)
        self.assertIs(sliced.data, sliced.calculator.data)
        self.assertIs(self.mea.electrode, sliced.electrode)
        # 元のインスタンスは変更されない (イミュータブル)
        self.assertEqual(0, self.mea.data.start)
        self.assertEqual(3, self.mea.data.end)

    def test_init_timeで時刻が0から始まる(self):
        sliced = self.mea.from_slice(1, 3).init_time()
        self.assertEqual(0, sliced.data.start)
        self.assertAlmostEqual(0, sliced.data.array[0][0])

    def test_down_samplingでサンプリングレートが下がる(self):
        down = self.mea.down_sampling(100)
        self.assertEqual(
            int(self.mea.data.SAMPLING_RATE / 100), down.data.SAMPLING_RATE
        )
        self.assertIs(down.data, down.fig.data)

    def test_iirnotch_filterで形状が維持される(self):
        filtered = self.mea.iirnotch_filter()
        self.assertEqual(self.mea.data.shape, filtered.data.shape)
        self.assertIs(filtered.data, filtered.calculator.data)

    def test_from_beat_cyclesで拍動周期ごとに分割される(self):
        peaks = detect_peak_neg(self.mea.data)
        beats = self.mea.from_beat_cycles(peaks, base_ch=32)

        self.assertEqual(len(peaks[32]), len(beats))
        for beat in beats:
            self.assertIs(beat.data, beat.fig.data)
            self.assertIs(beat.data, beat.calculator.data)

    def test_算術演算はndarrayに委譲される(self):
        added = self.mea + 1
        np.testing.assert_array_equal(self.mea.data.array + 1, added)
        self.assertEqual(len(self.mea.data.array), len(self.mea))


class TestMutableMEA(unittest.TestCase):
    def test_インスタンス化できる(self):
        # decode_hedの戻り値アンパックのバグ修正に対する回帰テスト
        path = fixture_hed_path("cardio")
        m = MutableMEA(path.__str__(), 0, 3)

        self.assertEqual(10000, m.SAMPLING_RATE)
        self.assertEqual(2000, m.GAIN)
        self.assertEqual((65, 30000), m.array.shape)
        self.assertEqual(3, m.time)


if __name__ == "__main__":
    unittest.main()
