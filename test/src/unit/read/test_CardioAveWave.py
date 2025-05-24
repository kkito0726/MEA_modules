import unittest
from test.utils import get_resource_path

from pyMEA import FilterType, read_MEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")
        self.front = 0.05
        self.back = 0.3

    def test_心筋細胞の波形データから平均波形を算出する(self):
        mea = read_MEA(self.path.__str__(), 0, 5, 450, FilterType.CARDIO_AVE_WAVE)
        self.assertEqual(
            (65, int((self.front + self.back) * mea.data.SAMPLING_RATE)), mea.data.shape
        )


if __name__ == "__main__":
    unittest.main()
