import unittest
from test.fixtures import fixture_hed_path

from pyMEA import FilterType, read_MEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = fixture_hed_path("cardio")

    def test_MEA計測データから移動平均を算出したインスタンスが生成できる(self):
        mea = read_MEA(self.path.__str__(), 0, 3, 450, FilterType.FILTER_MEA)
        self.assertEqual(
            (65, int(mea.data.time * mea.data.SAMPLING_RATE)), mea.data.shape
        )


if __name__ == "__main__":
    unittest.main()
