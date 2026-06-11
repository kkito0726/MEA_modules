import unittest

from pyMEA.domain.validators import ch_validator, get_argument, time_validator


@ch_validator
def func_with_ch(ch: int):
    return ch


@time_validator
def func_with_time(start: int, end: int):
    return start, end


def sample_func(a, b, c=3):
    return a + b + c


class TestChValidator(unittest.TestCase):
    def test_有効な電極番号はそのまま実行される(self):
        for ch in (1, 32, 64):
            self.assertEqual(ch, func_with_ch(ch))

    def test_範囲外の電極番号はValueErrorになる(self):
        for ch in (0, 65, -1, 100):
            with self.assertRaises(ValueError) as context:
                func_with_ch(ch)
            self.assertEqual(
                "chは1-64の整数で入力してください", str(context.exception)
            )


class TestTimeValidator(unittest.TestCase):
    def test_有効な時間範囲はそのまま実行される(self):
        self.assertEqual((0, 5), func_with_time(0, 5))
        self.assertEqual((1, 1), func_with_time(1, 1))

    def test_負の時間はValueErrorになる(self):
        with self.assertRaises(ValueError):
            func_with_time(-1, 5)
        with self.assertRaises(ValueError):
            func_with_time(0, -5)

    def test_startがendより大きい場合はValueErrorになる(self):
        with self.assertRaises(ValueError):
            func_with_time(5, 1)


class TestGetArgument(unittest.TestCase):
    def test_キーワード引数から値を取得できる(self):
        self.assertEqual(2, get_argument(sample_func, (), {"b": 2}, "b"))

    def test_位置引数から値を取得できる(self):
        self.assertEqual(1, get_argument(sample_func, (1, 2), {}, "a"))
        self.assertEqual(2, get_argument(sample_func, (1, 2), {}, "b"))

    def test_存在しない引数はNoneを返す(self):
        self.assertIsNone(get_argument(sample_func, (1,), {}, "z"))
        self.assertIsNone(get_argument(sample_func, (1,), {}, "c"))


if __name__ == "__main__":
    unittest.main()
