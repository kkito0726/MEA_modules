import inspect


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
