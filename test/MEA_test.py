import unittest
from pyMEA.MEA import MEA

class MyTestCase(unittest.TestCase):

    def test_MEA_instance(self):
        path = "./public/230615_day2_test_5s_.hed"
        start, end = 1, 2
        data = MEA(path, start, end)

        self.assertEqual(data.SAMPLING_RATE, 10000)  # add assertion here
        self.assertEqual(data.GAIN, 2000)
        self.assertEqual(data.shape, (65, 10000))

        for d in data:
            self.assertEqual(len(d), data.SAMPLING_RATE * data.time)


if __name__ == '__main__':
    unittest.main()
