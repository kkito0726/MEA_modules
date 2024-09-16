import unittest

from pyMEA import MEA, detect_peak_neg


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = "./public/230615_day2_test_5s_.hed"
        self.data = MEA(self.path, 0, 5)
        self.peak_index = detect_peak_neg(self.data.array)

    def test_something(self):
        for i in range(1, 65):
            for value in self.data[i][self.peak_index[i]]:
                self.assertTrue(value < -200)


if __name__ == "__main__":
    unittest.main()
