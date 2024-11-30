import unittest
from test.utils import get_resource_path

from pyMEA.read.MEA import MEA


class MEATest(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")

    def test_hedファイルからMEA計測データの読み込みができる(self):
        start, end = 1, 2
        data = MEA(self.path.__str__(), start, end)

        self.assertEqual(data.SAMPLING_RATE, 10000)  # add assertion here
        self.assertEqual(data.GAIN, 2000)
        self.assertEqual(data.shape, (65, int(data.time * data.SAMPLING_RATE)))

        for d in data:
            self.assertEqual(len(d), data.SAMPLING_RATE * data.time)

    def test_読み込み時刻が不正な場合例外が発生する(self):
        with self.assertRaises(ValueError) as context:
            MEA(self.path.__str__(), -1, 5)
        self.assertEqual(str(context.exception), "startとendは0以上のの整数で入力してください")

        with self.assertRaises(ValueError) as context:
            MEA(self.path.__str__(), 0, -5)
        self.assertEqual(str(context.exception), "startとendは0以上のの整数で入力してください")

        with self.assertRaises(ValueError) as context:
            MEA(self.path.__str__(), -1, -5)
        self.assertEqual(str(context.exception), "startとendは0以上のの整数で入力してください")

        with self.assertRaises(ValueError) as context:
            MEA(self.path.__str__(), 10, 5)
        self.assertEqual(str(context.exception), "start < endになるように入力してください")


if __name__ == "__main__":
    unittest.main()
