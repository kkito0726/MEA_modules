"""読み込みから解析・描画までの一連のワークフローを通す統合テスト。

従来の手動実行スクリプト (integration_test_*.py) のpytest版。
描画は isBuf=True でヘッドレス実行する。
"""

import unittest
from test.utils import get_resource_path

from pyMEA import FilterType, detect_peak_all, detect_peak_neg, read_MEA
from pyMEA.presentation.FigImage import FigImage


class TestNeuronWorkflow(unittest.TestCase):
    """神経データの解析ワークフロー"""

    @classmethod
    def setUpClass(cls):
        path = get_resource_path("230615_day2_test_5s_.hed")
        cls.mea = read_MEA(path.__str__(), 0, 5, 450)
        cls.neg_peaks = detect_peak_neg(cls.mea.data)
        cls.all_peaks = detect_peak_all(cls.mea.data)

    def test_読み込みからISI計算まで(self):
        isi = self.mea.calculator.isi(self.neg_peaks, ch=32)
        self.assertTrue((isi.values > 0).all())
        self.assertTrue(0 < isi.mean < 2)

    def test_読み込みから伝導速度計算まで(self):
        cv = self.mea.calculator.conduction_velocity(self.neg_peaks, 32, 33)
        self.assertTrue((cv.values > 0).all())

        gv = self.mea.calculator.gradient_velocity(self.neg_peaks)
        self.assertEqual(len(self.neg_peaks[32]), len(gv))

    def test_読み込みから描画まで(self):
        self.assertIsInstance(self.mea.fig.showAll(isBuf=True), FigImage)
        self.assertIsInstance(
            self.mea.fig.plotPeaks(32, self.neg_peaks, self.all_peaks, isBuf=True),
            FigImage,
        )

    def test_変換チェーンの結果でも解析できる(self):
        sub = self.mea.from_slice(1, 4).init_time()
        peaks = detect_peak_neg(sub.data)
        isi = sub.calculator.isi(peaks, ch=32)
        self.assertEqual(len(peaks[32]) - 1, len(isi))


class TestCardioWorkflow(unittest.TestCase):
    """心筋データの解析ワークフロー (平均波形フィルタ使用)"""

    @classmethod
    def setUpClass(cls):
        cls.path = get_resource_path("1102_dish3_day10_p210_5sec_.hed")

    def test_平均波形フィルタを通したFPD計算(self):
        mea = read_MEA(self.path.__str__(), 0, 5, 450, FilterType.CARDIO_AVE_WAVE)
        neg_peaks = detect_peak_neg(mea.data)
        fpd = mea.calculator.fpd(neg_peaks, ch=32)
        # FPDは設定した許容範囲内に収まる
        for value in fpd.values:
            self.assertTrue(0.1 < value < 0.4)

    def test_生データのままFPD計算(self):
        mea = read_MEA(self.path.__str__(), 0, 5, 450)
        neg_peaks = detect_peak_neg(mea.data)
        fpd = mea.calculator.fpd(neg_peaks, ch=32)
        self.assertGreaterEqual(len(fpd), 0)


if __name__ == "__main__":
    unittest.main()
