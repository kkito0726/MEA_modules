import unittest
from test.utils import get_resource_path

import numpy as np

from pyMEA import read_MEA


class MEATest(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")
        self.mea = read_MEA(self.path.__str__(), 0, 10, 450)

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

    def test_電位データのスライスができる(self):
        sliced_mea = self.mea.from_slice(0.5, 0.8)
        self.assertEqual(
            sliced_mea.data.shape, (65, int(0.3 * self.mea.data.SAMPLING_RATE))
        )
        self.assertEqual(sliced_mea.data.start, 0.5)
        self.assertEqual(sliced_mea.data.end, 0.8)
        self.assertEqual(round(sliced_mea.data.time, 2), 0.3)

    def test_時刻データの開始地点を0秒に初期化できる(self):
        sliced_mea = self.mea.from_slice(0.5, 0.8)
        init_time_mea = sliced_mea.init_time()

        self.assertEqual(
            init_time_mea.data.shape, (65, int(0.3 * self.mea.data.SAMPLING_RATE))
        )
        self.assertEqual(init_time_mea.data.start, 0)
        self.assertEqual(init_time_mea.data.end, 0.3)
        self.assertEqual(round(init_time_mea.data.time, 2), 0.3)

    def test_ダウンサンプリングができる(self):
        downsampled_mea = self.mea.down_sampling(100)
        self.assertEqual(downsampled_mea.data.shape, (65, 768))
        self.assertEqual(downsampled_mea.data.SAMPLING_RATE, 100)
        self.assertEqual(downsampled_mea.data.GAIN, self.mea.data.GAIN)
        self.assertEqual(downsampled_mea.data.start, self.mea.data.start)
        self.assertEqual(downsampled_mea.data.end, 7.68)

    def test_電位データを書き換えようとする場合_例外を発生する(self):
        with self.assertRaises(ValueError) as context:
            self.mea.data.array[5][200:300] = 0
        self.assertEqual("assignment destination is read-only", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.mea.data[16][200:300] = 0
        self.assertEqual("assignment destination is read-only", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.mea[58][200:300] = 0
        self.assertEqual("assignment destination is read-only", str(context.exception))


if __name__ == "__main__":
    unittest.main()
