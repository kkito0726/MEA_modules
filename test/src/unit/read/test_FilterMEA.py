import unittest
from test.utils import get_resource_path

from pyMEA.read.FilterMEA import FilterMEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")

    def test_MEA計測データから移動平均を算出したインスタンスが生成できる(self):
        data = FilterMEA(self.path.__str__(), 0, 5)
        self.assertEqual((65, int(data.time * data.SAMPLING_RATE)), data.shape)


if __name__ == "__main__":
    unittest.main()
