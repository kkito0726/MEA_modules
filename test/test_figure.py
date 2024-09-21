import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.MEA import MEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = "./public/230615_day2_test_5s_.hed"
        self.data = MEA(self.path, 0, 5)
        self.peak_index = detect_peak_neg(self.data.array)

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.plot")
    def test_64電極表示できる(self, mock_plot: MagicMock, mock_show: MagicMock):
        self.data.showAll()
        for ch in range(1, 65):
            x_actual, y_actual = mock_plot.call_args_list[ch - 1][0]
            # numpyの配列比較を行う
            np.testing.assert_array_equal(x_actual, self.data.array[0])
            np.testing.assert_array_equal(y_actual, self.data.array[ch])

        self.assertEqual(mock_show.call_count, 1)

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.plot")
    def test_1電極表示できる(self, mock_plot: MagicMock, mock_show: MagicMock):
        for ch in range(1, 65):
            self.data.showSingle(ch)

            x_actual, y_actual = mock_plot.call_args_list[ch - 1][0]
            # numpyの配列比較を行う
            np.testing.assert_array_equal(x_actual, self.data.array[0])
            np.testing.assert_array_equal(y_actual, self.data.array[ch])
        # showが呼び出された回数を確認
        self.assertEqual(mock_show.call_count, 64)


if __name__ == "__main__":
    unittest.main()
