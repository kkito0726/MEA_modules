import tempfile
import unittest
from pathlib import Path
from test.fixtures import fixture_hed_path

from pyMEA import read_MEA
from pyMEA.presentation.plot.color import normalize_color
from pyMEA.presentation.plot.pointcare_plot import autocorrelation, normalize_data


class TestNormalizeColor(unittest.TestCase):
    def test_Noneはデフォルトカラーのリストになる(self):
        self.assertEqual([None], normalize_color(None))
        self.assertEqual(["red"], normalize_color(None, "red"))

    def test_文字列は単一要素リストになる(self):
        self.assertEqual(["blue"], normalize_color("blue"))

    def test_RGB値1セットは入れ子リストになる(self):
        self.assertEqual([[0.1, 0.2, 0.3]], normalize_color([0.1, 0.2, 0.3]))

    def test_リストはそのまま返る(self):
        self.assertEqual(["r", "g"], normalize_color(["r", "g"]))
        self.assertEqual([[0.1, 0.2], [0.3, 0.4]], normalize_color([[0.1, 0.2], [0.3, 0.4]]))

    def test_不正な型はTypeErrorになる(self):
        with self.assertRaises(TypeError):
            normalize_color(123)


class TestPointcareUtils(unittest.TestCase):
    def test_正規化で指定範囲に収まる(self):
        normalized = normalize_data([1.0, 2.0, 3.0])
        self.assertAlmostEqual(-1, normalized.min())
        self.assertAlmostEqual(1, normalized.max())

    def test_自己相関係数が計算できる(self):
        import numpy as np

        # 一定値からの線形増加データはラグ0で正の自己相関を持つ
        data = np.sin(np.linspace(0, 4 * np.pi, 100))
        r = autocorrelation(data, 0)
        self.assertTrue(-1 <= r <= 1)


class TestVideoMEA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = fixture_hed_path("cardio")
        cls.mea = read_MEA(path.__str__(), 1, 2, 450)

    def test_GIFを保存できる(self):
        from pyMEA import detect_peak_neg

        peaks = detect_peak_neg(self.mea.data)
        video = self.mea.fig.draw_2d(peaks, mesh_num=10, dpi=50, isBuf=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            gif_path = Path(tmpdir) / "output.gif"
            video.save_gif(str(gif_path))
            self.assertTrue(gif_path.exists())
            self.assertGreater(gif_path.stat().st_size, 0)

    def test_拡張子が不正な場合はValueErrorになる(self):
        from pyMEA import detect_peak_neg

        peaks = detect_peak_neg(self.mea.data)
        video = self.mea.fig.draw_2d(peaks, mesh_num=10, dpi=50, isBuf=True)

        with self.assertRaises(ValueError):
            video.save_gif("./output.png")
        with self.assertRaises(ValueError):
            video.save_mp4("./output.gif")

    def test_FigImageを画像ファイルに保存できる(self):
        img = self.mea.fig.showSingle(32, isBuf=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            png_path = Path(tmpdir) / "output.png"
            img.save(str(png_path))
            self.assertTrue(png_path.exists())

            with self.assertRaises(ValueError):
                img.save(str(Path(tmpdir) / "output.bmp"))


if __name__ == "__main__":
    unittest.main()
