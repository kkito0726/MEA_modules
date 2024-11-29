import unittest

from pyMEA import FigMEA
from pyMEA.read.FilterMEA import FilterMEA, MEA


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = "./public/230615_day2_test_5s_.hed"

    def test_something(self):
        data = FilterMEA(self.path, 0, 5)
        self.assertEqual(data.shape, (65, 50000))

if __name__ == '__main__':
    unittest.main()
