import unittest
from test.utils import get_resource_path

from pyMEA import FilterType, read_MEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")

    def test_MEA計測データから移動平均を算出したインスタンスが生成できる(self):
        mea = read_MEA(self.path.__str__(), 0, 5, 450, FilterType.FILTER_MEA)
        self.assertEqual(
            (65, int(mea.data.time * mea.data.SAMPLING_RATE)), mea.data.shape
        )


if __name__ == "__main__":
    unittest.main()
