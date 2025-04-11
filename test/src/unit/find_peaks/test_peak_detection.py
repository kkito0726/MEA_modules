import unittest
from test.utils import get_resource_path

from pyMEA import detect_peak_all, detect_peak_neg
from pyMEA.find_peaks.peak_detection import detect_peak_pos
from pyMEA.read.model.MEA import MEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")
        self.data = MEA(self.path.__str__(), 0, 5)
        self.neg_peak_index = detect_peak_neg(self.data)
        self.pos_peak_index = detect_peak_pos(self.data, height=(200, 50000))
        self.all_peak_index = detect_peak_all(self.data)

    def test_下方向のピークを抽出できる(self):
        for i in range(1, 65):
            for value in self.data[i][self.neg_peak_index[i]]:
                self.assertTrue(value < -200)

    def test_上方向のピークを抽出できる(self):
        for i in range(1, 65):
            for value in self.data[i][self.pos_peak_index[i]]:
                self.assertTrue(value > 200)


if __name__ == "__main__":
    unittest.main()
