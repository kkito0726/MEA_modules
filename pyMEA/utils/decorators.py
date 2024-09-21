import inspect
from functools import wraps


def channel(func):
    def wrapper(*args, **kwargs):
        if kwargs.get("ch"):
            ch = kwargs.get("ch")
        else:
            ch = args[1]
        print(f"ch {ch}")

        func(*args, **kwargs)

        print("=====================")

    return wrapper


def ch_validator(func):
    def wrapper(*args, **kwargs):
        # 関数のシグネチャを取得
        sig = inspect.signature(func)
        params = sig.parameters

        # 位置引数とキーワード引数の両方で 'ch' で始まる引数を探す
        param_names = list(params.keys())
        for i, param_name in enumerate(param_names):
            if param_name.startswith("ch"):
                # キーワード引数として存在するか確認
                ch = kwargs.get(param_name)

                # 位置引数として存在するか確認
                if ch is None and i < len(args):
                    ch = args[i]

                # 'ch' のバリデーション
                if ch is not None:
                    if not (1 <= ch <= 64):
                        raise ValueError(f"{param_name}は1-64の整数で入力してください")

        return func(*args, **kwargs)

    return wrapper


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
