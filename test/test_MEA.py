import unittest
from array import array

from pyMEA.MEA import MEA


class MEATest(unittest.TestCase):
    def test_hedファイルからMEA計測データの読み込みができる(self):
        path = "./public/230615_day2_test_5s_.hed"
        start, end = 1, 2
        data = MEA(path, start, end)

        self.assertEqual(data.SAMPLING_RATE, 10000)  # add assertion here
        self.assertEqual(data.GAIN, 2000)
        self.assertEqual(data.shape, (65, 10000))

        for d in data:
            self.assertEqual(len(d), data.SAMPLING_RATE * data.time)

    def test_読み込み時刻が不正な場合例外が発生する(self):
        path = "./public/230615_day2_test_5s_.hed"

        with self.assertRaises(ValueError) as context:
            MEA(path, -1, 5)
        self.assertEqual(str(context.exception), "startとendは0以上のの整数で入力してください")

        with self.assertRaises(ValueError) as context:
            MEA(path, 0, -5)
        self.assertEqual(str(context.exception), "startとendは0以上のの整数で入力してください")

        with self.assertRaises(ValueError) as context:
            MEA(path, -1, -5)
        self.assertEqual(str(context.exception), "startとendは0以上のの整数で入力してください")

        with self.assertRaises(ValueError) as context:
            MEA(path, 10, 5)
        self.assertEqual(str(context.exception), "start < endになるように入力してください")


if __name__ == "__main__":
    unittest.main()
