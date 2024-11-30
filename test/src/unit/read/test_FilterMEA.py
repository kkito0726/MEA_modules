import unittest

from pyMEA.read.FilterMEA import FilterMEA
from test.utils import get_resource_path


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.path = get_resource_path("230615_day2_test_5s_.hed")

    def test_something(self):
        data = FilterMEA(self.path.__str__(), 0, 5)
        self.assertEqual(data.shape, (65, 50000))

if __name__ == '__main__':
    unittest.main()
