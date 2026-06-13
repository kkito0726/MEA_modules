"""float32メモリ保持と時刻軸float64精度の回帰テスト。

電位データは float32 で保持してメモリを半減しつつ、時刻軸は float64 で
再生成して長時間記録でも精度を保つこと(分離設計)を担保する。
"""

import unittest
from test.fixtures import fixture_hed_path

import numpy as np

from pyMEA import read_MEA
from pyMEA.domain.model.HedPath import HedPath
from pyMEA.domain.model.MEA import MEA


class MEADtypeTest(unittest.TestCase):
    def setUp(self):
        self.path = fixture_hed_path("cardio")
        self.mea = read_MEA(self.path.__str__(), 0, 3, 450)

    def test_電位データはfloat32で保持される(self):
        # メモリ半減の根拠: 保持配列が float32
        self.assertEqual(np.float32, self.mea.data.array.dtype)

    def test_時刻軸はfloat64で配信される(self):
        # 時刻行 [0] は精度確保のため float64 の times を返す
        self.assertEqual(np.float64, self.mea.data[0].dtype)
        self.assertEqual(np.float64, self.mea.data.times.dtype)

    def test_時刻軸は正確な等間隔になる(self):
        diffs = np.diff(self.mea.data[0])
        expected = 1 / self.mea.data.SAMPLING_RATE
        np.testing.assert_allclose(diffs, expected, rtol=0, atol=1e-12)

    def test_開始時刻が大きい長時間記録でも時刻が潰れない(self):
        # float32 だと start=3600s で隣接サンプルが同値に潰れるが、
        # times は float64 再生成のため潰れないこと(崩壊ケースなし)
        sr = 10000
        n = sr  # 1秒ぶん
        dummy = np.zeros((65, n), dtype=np.float64)
        mea = MEA(HedPath("cardio.hed"), 3600, 3601, sr, 2000, dummy)

        diffs = np.diff(mea[0])
        # すべての隣接サンプルが厳密に 1/sr 間隔(潰れ=0)
        self.assertEqual(0, int(np.sum(diffs == 0)))
        np.testing.assert_allclose(diffs, 1 / sr, rtol=0, atol=1e-12)

    def test_shapeは65行を維持する(self):
        self.assertEqual(65, self.mea.data.shape[0])

    def test_電位配列は読み取り専用(self):
        with self.assertRaises(ValueError):
            self.mea.data.array[1][0:10] = 0

    def test_iirnotch後もfloat32保持かつ時刻float64(self):
        filtered = self.mea.data.iirnotch_filter()
        self.assertEqual(np.float32, filtered.array.dtype)
        self.assertEqual(np.float64, filtered[0].dtype)


if __name__ == "__main__":
    unittest.main()
