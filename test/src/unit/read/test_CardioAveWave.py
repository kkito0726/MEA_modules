import unittest
from test.utils import get_resource_path

from pyMEA import CardioAveWave


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")
        self.front = 0.05
        self.back = 0.3

    def test_心筋細胞の波形データから平均波形を算出する(self):
        data = CardioAveWave(self.path.__str__(), 0, 5)
        self.assertEqual(data.shape, (65, int((self.front+self.back) * data.SAMPLING_RATE)))


if __name__ == "__main__":
    unittest.main()
