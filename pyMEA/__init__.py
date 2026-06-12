"""pyMEA - MEA計測データの読み込み・解析ライブラリ。

公開APIはこのモジュールから直接インポートする (from pyMEA import *)。
重い依存 (matplotlib等) を必要時のみ読み込むため、PEP 562の遅延importで
エクスポートしている。公開名・シグネチャは従来と互換。
"""

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyMEA.application.read_MEA import read_MEA
    from pyMEA.domain.model.FilterType import FilterType
    from pyMEA.domain.model.MEA import MEA
    from pyMEA.application.MutableMEA import MutableMEA
    from pyMEA.domain.service.calculator import Calculator
    from pyMEA.domain.service.peak_detection import (
        detect_peak_all,
        detect_peak_neg,
        detect_peak_pos,
    )
    from pyMEA.presentation.FigMEA import FigMEA
    from pyMEA.presentation.video import VideoMEA

# 公開名 -> 定義モジュールのマッピング
_EXPORTS = {
    "read_MEA": "pyMEA.application.read_MEA",
    "FilterType": "pyMEA.domain.model.FilterType",
    "MEA": "pyMEA.domain.model.MEA",
    "MutableMEA": "pyMEA.application.MutableMEA",
    "Calculator": "pyMEA.domain.service.calculator",
    "detect_peak_neg": "pyMEA.domain.service.peak_detection",
    "detect_peak_pos": "pyMEA.domain.service.peak_detection",
    "detect_peak_all": "pyMEA.domain.service.peak_detection",
    "FigMEA": "pyMEA.presentation.FigMEA",
    "VideoMEA": "pyMEA.presentation.video",
}

__all__ = [
    "read_MEA",
    "FilterType",
    "MEA",
    "MutableMEA",
    "FigMEA",
    "VideoMEA",
    "Calculator",
    "detect_peak_neg",
    "detect_peak_pos",
    "detect_peak_all",
]


def __getattr__(name: str):
    if name in _EXPORTS:
        module = importlib.import_module(_EXPORTS[name])
        value = getattr(module, name)
        globals()[name] = value  # 2回目以降のアクセスを高速化するためキャッシュ
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
