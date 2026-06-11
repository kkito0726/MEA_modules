"""描画出力用のデコレータ。

matplotlibに依存するためpresentation層に置く。
入力バリデーション用のデコレータは pyMEA.domain.validators にある。
"""

import io

import matplotlib.pyplot as plt

from pyMEA.domain.validators import get_argument
from pyMEA.presentation.FigImage import FigImage


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
