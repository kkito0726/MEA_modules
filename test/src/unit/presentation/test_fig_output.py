import unittest
from test.utils import get_resource_path

from pyMEA import detect_peak_neg, read_MEA
from pyMEA.presentation.FigImage import FigImage
from pyMEA.presentation.video import VideoMEA


class TestFigMEABufferOutput(unittest.TestCase):
    """全描画メソッドが isBuf=True で FigImage / VideoMEA を返すことを保証する。"""

    @classmethod
    def setUpClass(cls):
        path = get_resource_path("230615_day2_test_5s_.hed")
        cls.mea = read_MEA(path.__str__(), 1, 2, 450)
        cls.peaks = detect_peak_neg(cls.mea.data)

    def test_波形描画はFigImageを返す(self):
        self.assertIsInstance(self.mea.fig.showAll(isBuf=True), FigImage)
        self.assertIsInstance(self.mea.fig.showSingle(32, isBuf=True), FigImage)
        self.assertIsInstance(
            self.mea.fig.plotPeaks(32, self.peaks, isBuf=True), FigImage
        )
        self.assertIsInstance(self.mea.fig.plot_spectrum(32, isBuf=True), FigImage)
        self.assertIsInstance(
            self.mea.fig.showDetection([31, 32, 33], isBuf=True), FigImage
        )

    def test_ラスタプロットとヒストグラムはFigImageを返す(self):
        self.assertIsInstance(
            self.mea.fig.raster_plot(self.peaks, [31, 32, 33], isBuf=True), FigImage
        )
        self.assertIsInstance(
            self.mea.fig.mkHist(self.peaks, [31, 32, 33], isBuf=True), FigImage
        )

    def test_カラーマップはVideoMEAを返す(self):
        video = self.mea.fig.draw_2d(self.peaks, mesh_num=20, isBuf=True)
        self.assertIsInstance(video, VideoMEA)
        self.assertEqual(len(self.peaks[32]), len(video))

        video3d = self.mea.fig.draw_3d(self.peaks, mesh_num=20, isBuf=True)
        self.assertIsInstance(video3d, VideoMEA)

    def test_値オブジェクトの描画はFigImageを返す(self):
        isi = self.mea.calculator.isi(self.peaks, ch=32)
        self.assertIsInstance(isi.show(isBuf=True), FigImage)


if __name__ == "__main__":
    unittest.main()
