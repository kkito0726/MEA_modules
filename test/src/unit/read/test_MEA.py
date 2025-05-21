import unittest
from test.utils import get_resource_path

import numpy as np

from pyMEA import read_MEA


class MEATest(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")

    def test_hedファイルからMEA計測データの読み込みができる(self):
        start, end = 1, 2
        mea = read_MEA(self.path.__str__(), start, end, 450)

        self.assertEqual(10000, mea.data.SAMPLING_RATE)  # add assertion here
        self.assertEqual(2000, mea.data.GAIN)
        self.assertEqual(
            (65, int(mea.data.time * mea.data.SAMPLING_RATE)), mea.data.shape
        )
        self.assertEqual(
            f"""読み込み開始時間  : {mea.data.start} s
読み込み終了時間  : {mea.data.end} s
読み込み合計時間  : {mea.data.time} s
サンプリングレート: {mea.data.SAMPLING_RATE} Hz
GAIN           : {mea.data.GAIN}""",
            mea.data.info,
        )
        # data[0]に時刻データが入っていること
        for diff in np.diff(mea.data[0]):
            self.assertEqual(1 / mea.data.SAMPLING_RATE, round(diff, 4))
        for d in mea.data:
            self.assertEqual(mea.data.SAMPLING_RATE * mea.data.time, len(d))

    def test_読み込み時刻が不正な場合例外が発生する(self):
        with self.assertRaises(ValueError) as context:
            read_MEA(self.path.__str__(), -1, 5, 450)
        self.assertEqual(
            "startとendは0以上のの整数で入力してください", str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            read_MEA(self.path.__str__(), 0, -5, 450)
        self.assertEqual(
            "startとendは0以上のの整数で入力してください", str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            read_MEA(self.path.__str__(), -1, -5, 450)
        self.assertEqual(
            "startとendは0以上のの整数で入力してください", str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            read_MEA(self.path.__str__(), 10, 5, 450)
        self.assertEqual(
            "start < endになるように入力してください", str(context.exception)
        )

    def test_hedファイル以外のファイルパスを入力する場合_例外発生する(self):
        with self.assertRaises(ValueError) as context:
            read_MEA("/User/your/mea_data.bio", 0, 5, 450)
        self.assertEqual(".hedファイルのパスを入力してください", str(context.exception))


if __name__ == "__main__":
    unittest.main()
