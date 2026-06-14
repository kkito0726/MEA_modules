"""save_npz / read_MEA_npz のラウンドトリップと容量削減の回帰テスト。"""

import os
import tempfile
import unittest
from test.fixtures import fixture_hed_path

import numpy as np

from pyMEA import read_MEA, read_MEA_npz
from pyMEA.infrastructure.reader import create_reader


class NpzIoTest(unittest.TestCase):
    def setUp(self):
        self.path = fixture_hed_path("cardio")
        self.pymea = read_MEA(self.path.__str__(), 0, 3, 450)
        self._tmp = tempfile.TemporaryDirectory()
        self.npz = os.path.join(self._tmp.name, "data.npz")

    def tearDown(self):
        self._tmp.cleanup()

    def test_float32保存は電位を完全一致で復元する(self):
        self.pymea.save_npz(self.npz, dtype="float32")
        loaded = read_MEA_npz(self.npz, 450)

        np.testing.assert_array_equal(
            self.pymea.data.array[1:], loaded.data.array[1:]
        )

    def test_int16保存は16bit精度で復元する(self):
        self.pymea.save_npz(self.npz, dtype="int16")
        loaded = read_MEA_npz(self.npz, 450)

        orig = self.pymea.data.array[1:]
        scale = float(np.max(np.abs(orig))) / 32767
        np.testing.assert_allclose(orig, loaded.data.array[1:], rtol=0, atol=scale)

    def test_メタ情報が復元される(self):
        self.pymea.save_npz(self.npz, dtype="float32")
        loaded = read_MEA_npz(self.npz, 450)

        self.assertEqual(self.pymea.data.SAMPLING_RATE, loaded.data.SAMPLING_RATE)
        self.assertEqual(self.pymea.data.GAIN, loaded.data.GAIN)
        self.assertEqual(self.pymea.data.start, loaded.data.start)
        self.assertEqual(self.pymea.data.end, loaded.data.end)
        self.assertEqual(self.pymea.data.shape, loaded.data.shape)

    def test_時刻行はfloat64で再生成される(self):
        self.pymea.save_npz(self.npz, dtype="float32")
        loaded = read_MEA_npz(self.npz, 450)

        self.assertEqual(np.float64, loaded.data[0].dtype)
        np.testing.assert_array_equal(self.pymea.data[0], loaded.data[0])

    def test_容量はfloat64比で削減される(self):
        f32 = os.path.join(self._tmp.name, "f32.npz")
        i16 = os.path.join(self._tmp.name, "i16.npz")
        self.pymea.save_npz(f32, dtype="float32")
        self.pymea.save_npz(i16, dtype="int16")

        raw_f64 = self.pymea.data.array.astype(np.float64).nbytes
        size_f32 = os.path.getsize(f32)
        size_i16 = os.path.getsize(i16)

        # 圧縮込みで float64 生サイズより十分小さく、int16 < float32
        self.assertLess(size_f32, raw_f64 * 0.6)
        self.assertLess(size_i16, size_f32)

    def test_デフォルトはint16保存(self):
        # 既定 dtype は int16(容量優先)。float32明示時と容量が変わることで確認する
        default_path = os.path.join(self._tmp.name, "default.npz")
        f32_path = os.path.join(self._tmp.name, "explicit_f32.npz")
        self.pymea.save_npz(default_path)                      # 既定
        self.pymea.save_npz(f32_path, dtype="float32")

        with np.load(default_path) as d:
            self.assertEqual("int16", str(d["dtype"]))
        # 既定(int16)は float32 明示より小さい
        self.assertLess(os.path.getsize(default_path), os.path.getsize(f32_path))

    def test_未対応拡張子は例外(self):
        with self.assertRaises(ValueError) as ctx:
            create_reader("data.txt")
        self.assertIn("未対応の拡張子", str(ctx.exception))

    def test_dtype不正は例外(self):
        with self.assertRaises(ValueError):
            self.pymea.save_npz(self.npz, dtype="float16")


if __name__ == "__main__":
    unittest.main()
