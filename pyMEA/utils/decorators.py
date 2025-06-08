import inspect
import io
from functools import wraps

import matplotlib.pyplot as plt

from pyMEA.figure.video import FigImage


def channel(func):
    def wrapper(*args, **kwargs):
        isBuf = get_argument(func, args, kwargs, "isBuf")
        if isBuf:
            return func(*args, **kwargs)
        if kwargs.get("ch"):
            ch = kwargs.get("ch")
        else:
            ch = args[1]
        print(f"ch {ch}")

        result = func(*args, **kwargs)

        print("=====================")
        return result

    return wrapper


def ch_validator(func):
    def wrapper(*args, **kwargs):
        ch = get_argument(func, args, kwargs, "ch")

        # 'ch' のバリデーション
        if ch is not None:
            if not (1 <= ch <= 64):
                raise ValueError("chは1-64の整数で入力してください")

        return func(*args, **kwargs)

    return wrapper


def get_argument(func, args, kwargs, arg_name):
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    if arg_name in kwargs:
        return kwargs[arg_name]

    try:
        index = params.index(arg_name)
        if index < len(args):
            return args[index]
    except ValueError:
        pass

    return None


def time_validator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 関数の引数名を取得
        sig = inspect.signature(func)

        # argsをkwargsに変換（位置引数を名前付き引数に変換）
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()

        # 'start' と 'end' の引数を取得
        start = bound_args.arguments.get("start")
        end = bound_args.arguments.get("end")

        # バリデーション
        if start < 0 or end < 0:
            raise ValueError("startとendは0以上のの整数で入力してください")
        if start > end:
            raise ValueError("start < endになるように入力してください")

        # 条件を満たしていれば関数を実行
        return func(*args, **kwargs)

    return wrapper


def output_buf(func):
    def wrapper(*args, **kwargs):
        isBuf = get_argument(func, args, kwargs, "isBuf")
        # 描画実行
        result = func(*args, **kwargs)

        if isBuf:
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png")
            buf.seek(0)
            plt.close()
            return FigImage(buf)
        else:
            plt.show()
            plt.close()
            return result

    return wrapper
