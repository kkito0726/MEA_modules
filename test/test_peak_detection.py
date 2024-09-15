import unittest

from pyMEA import MEA, detect_peak_neg

path = "./public/230615_day2_test_5s_.hed"
data = MEA(path, 0, 5)
peak_index = detect_peak_neg(data.array)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        for i in range(1, 65):
            for value in data[i][peak_index[i]]:
                self.assertTrue(value < -200)


if __name__ == "__main__":
    unittest.main()
