import unittest
from test.utils import get_resource_path

from pyMEA import detect_peak_neg, read_MEA
from pyMEA.domain.service.CardioAveWave import calc_64_ave_waves
from pyMEA.domain.service.FilterMEA import filter_by_moving_average


class TestFilterMEA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = get_resource_path("230615_day2_test_5s_.hed")
        cls.mea = read_MEA(path.__str__(), 0, 5, 450)

    def test_移動平均フィルタ後も形状が維持される(self):
        filtered = filter_by_moving_average(self.mea.data)
        self.assertEqual(self.mea.data.shape, filtered.shape)

    def test_フィルタは元データを変更しない(self):
        before = self.mea.data.array.copy()
        filter_by_moving_average(self.mea.data)
        self.assertTrue((before == self.mea.data.array).all())


class TestCardioAveWave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = get_resource_path("1102_dish3_day10_p210_5sec_.hed")
        cls.mea = read_MEA(path.__str__(), 0, 5, 450)
        cls.neg_peaks = detect_peak_neg(cls.mea.data)

    def test_平均波形は指定時間幅の形状になる(self):
        front, back = 0.05, 0.3
        ave_waves = calc_64_ave_waves(self.mea.data, self.neg_peaks, front, back)

        expected_frames = int(self.mea.data.SAMPLING_RATE * (front + back))
        self.assertEqual((65, expected_frames), ave_waves.shape)
        # 時間データは0から始まる
        self.assertEqual(0, ave_waves[0][0])


if __name__ == "__main__":
    unittest.main()
