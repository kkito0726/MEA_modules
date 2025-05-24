import unittest
from test.utils import get_resource_path
from unittest.mock import MagicMock, patch

import numpy as np

from pyMEA import read_MEA
from pyMEA.core.Electrode import Electrode
from pyMEA.figure.FigMEA import FigMEA
from pyMEA.figure.plot.plot import circuit_eles
from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.read.model.MEA import MEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")
        self.mea = read_MEA(self.path.__str__(), 1, 2, 450)
        self.peak_index = detect_peak_neg(self.mea.data)
        self.fm = FigMEA(self.mea.data, Electrode(450))

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.plot")
    def test_64電極表示できる(self, mock_plot: MagicMock, mock_show: MagicMock):
        self.fm.showAll()
        for ch in range(1, 65):
            x_actual, y_actual = mock_plot.call_args_list[ch - 1][0]
            # numpyの配列比較を行う
            np.testing.assert_array_equal(x_actual, self.mea.data.array[0])
            np.testing.assert_array_equal(y_actual, self.mea.data.array[ch])

        self.assertEqual(mock_show.call_count, 1)

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.plot")
    def test_1電極表示できる(self, mock_plot: MagicMock, mock_show: MagicMock):
        for ch in range(1, 65):
            self.fm.showSingle(ch)

            x_actual, y_actual = mock_plot.call_args_list[ch - 1][0]
            # numpyの配列比較を行う
            np.testing.assert_array_equal(x_actual, self.mea.data.array[0])
            np.testing.assert_array_equal(y_actual, self.mea.data.array[ch])
        # showが呼び出された回数を確認
        self.assertEqual(mock_show.call_count, 64)

    @patch("matplotlib.pyplot.show")
    def test_AMC経路のカラーマップ描画(self, mock_show: MagicMock):
        original_method = self.fm.data.from_beat_cycles
        with patch.object(
            MEA, "from_beat_cycles", side_effect=original_method
        ) as mock_method:
            self.fm.draw_line_conduction(self.peak_index, circuit_eles)
        mock_method.assert_not_called()
        mock_show.assert_called_once()

    @patch("matplotlib.pyplot.show")
    def test_AMC経路のカラーマップ描画_拍動周期ごとにピーク抽出(
        self, mock_show: MagicMock
    ):
        original_method = self.fm.data.from_beat_cycles
        with patch.object(
            MEA, "from_beat_cycles", side_effect=original_method
        ) as mock_method:
            self.fm.draw_line_conduction(self.peak_index, circuit_eles, 8)
        mock_method.assert_called()
        mock_show.assert_called_once()

    def test_AMC経路のカラーマップ描画するときにAMC電極以外の電極が基準電極に指定される時エラーになる(
        self,
    ):
        with self.assertRaises(ValueError) as context:
            self.fm.draw_line_conduction(self.peak_index, circuit_eles, 18)
        self.assertEqual(
            "基準電極はAMC内の電極から選択してください", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
