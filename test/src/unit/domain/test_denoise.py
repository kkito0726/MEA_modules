import unittest
from test.fixtures import fixture_hed_path

import numpy as np

from pyMEA import FilterType, detect_peak_neg, read_MEA


class TestDenoiseFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mea = read_MEA(fixture_hed_path("cardio").__str__(), 0, 3, 450)

    def _quiet_rms(self, mea, ch, halfwin_ms=15):
        sr = mea.SAMPLING_RATE
        spikes = np.asarray(detect_peak_neg(mea)[ch])
        h = int(halfwin_ms * sr / 1000)
        mask = np.zeros(mea.array.shape[1], bool)
        for p in spikes:
            mask[max(0, p - h) : p + h] = True
        return mea.array[ch][~mask].std()

    # ---- 形状・イミュータブル ----
    def test_各手法とも形状と時刻行を保持する(self):
        for filtered in (
            self.mea.data.highpass(1),
            self.mea.data.bandpass(1, 1000),
            self.mea.data.common_median_reference(),
            self.mea.data.wavelet_denoise(),
        ):
            self.assertEqual(self.mea.data.shape, filtered.shape)
            np.testing.assert_allclose(filtered.array[0], self.mea.data.array[0])

    def test_ウェーブレットはノイズを下げスパイクを保つ(self):
        ch = 6
        denoised = self.mea.data.wavelet_denoise()
        # 静穏区間のノイズが下がる
        self.assertLess(self._quiet_rms(denoised, ch), self._quiet_rms(self.mea.data, ch))
        # 強信号ではスパイク検出が維持される
        raw = np.asarray(detect_peak_neg(self.mea.data)[ch])
        dn = np.asarray(detect_peak_neg(denoised)[ch])
        self.assertEqual(len(raw), len(dn))

    def test_元データを変更せず新インスタンスを返す(self):
        before = self.mea.data.array.copy()
        result = self.mea.data.highpass(1)
        self.assertIsNot(result, self.mea.data)
        self.assertTrue((before == self.mea.data.array).all())

    # ---- ゼロ位相: タイミング不変 ----
    def test_ハイパスはピークタイミングを変えない(self):
        ch = 6
        raw = np.asarray(detect_peak_neg(self.mea.data)[ch])
        hp = np.asarray(detect_peak_neg(self.mea.data.highpass(1))[ch])
        self.assertEqual(len(raw), len(hp))
        self.assertEqual(0, int(np.max(np.abs(raw - hp))))

    def test_バンドパスはピークタイミングをほぼ変えない(self):
        ch = 6
        raw = np.asarray(detect_peak_neg(self.mea.data)[ch])
        bp = np.asarray(detect_peak_neg(self.mea.data.bandpass(1, 1000))[ch])
        self.assertEqual(len(raw), len(bp))
        # ゼロ位相のため数フレーム以内
        self.assertLessEqual(int(np.max(np.abs(raw - bp))), 5)

    # ---- ノイズ低減 ----
    def test_バンドパスは静穏区間のノイズを下げる(self):
        ch = 6
        self.assertLess(
            self._quiet_rms(self.mea.data.bandpass(1, 1000), ch),
            self._quiet_rms(self.mea.data, ch),
        )

    def test_CMRは共通モードノイズを除去する(self):
        # 全電極に共通の正弦波ノイズを加え、CMRで除去できることを確認
        sr = self.mea.data.SAMPLING_RATE
        t = self.mea.data.array[0]
        common = 50 * np.sin(2 * np.pi * 50 * t)
        noisy = self.mea.data.array.copy()
        noisy[1:65] += common
        from pyMEA.domain.model.MEA import MEA

        noisy_mea = MEA(
            self.mea.data.hed_path, 0, 3, sr, self.mea.data.GAIN, noisy
        )
        cleaned = noisy_mea.common_median_reference()
        # 共通ノイズ付加でRMSが増え、CMRで元水準近くまで戻る
        ch = 6
        self.assertLess(
            self._quiet_rms(cleaned, ch), self._quiet_rms(noisy_mea, ch)
        )


class TestDenoisePresetsAndSNR(unittest.TestCase):
    def _snr(self, mea, ch):
        return mea.calculator.snr(detect_peak_neg(mea.data), ch)

    def test_snrは正の値を返す(self):
        mea = read_MEA(fixture_hed_path("cardio").__str__(), 0, 3, 450)
        self.assertGreater(self._snr(mea, 6), 0)

    def test_心筋デノイズプリセットでSN比が改善する(self):
        path = fixture_hed_path("cardio").__str__()
        raw = read_MEA(path, 0, 3, 450)
        den = read_MEA(path, 0, 3, 450, FilterType.CARDIO_DENOISE)
        self.assertEqual(raw.data.shape, den.data.shape)
        self.assertGreater(self._snr(den, 6), self._snr(raw, 6))

    def test_微弱心筋プリセットが適用でき形状を保つ(self):
        path = fixture_hed_path("cardio").__str__()
        den = read_MEA(path, 0, 3, 450, FilterType.CARDIO_DENOISE_WEAK)
        self.assertEqual((65, 30000), den.data.shape)
        self.assertGreater(self._snr(den, 6), 0)

    def test_神経デノイズプリセットが適用できる(self):
        path = fixture_hed_path("neuro").__str__()
        raw = read_MEA(path, 0, 3, 450)
        den = read_MEA(path, 0, 3, 450, FilterType.NEURO_DENOISE)
        self.assertEqual(raw.data.shape, den.data.shape)


if __name__ == "__main__":
    unittest.main()
