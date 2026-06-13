"""MEA計測データの .npz 保存。

電位データを float32(実質無損失) / int16(16bit量子化) で圧縮保存する。
時刻行は start/SAMPLING_RATE/列数から復元できるため保存しない(冗長排除)。
"""

import numpy as np

from pyMEA.domain.model.MEA import MEA

# .npz 内のキー(読込側 reader.py と共有)
KEY_HED_PATH = "hed_path"
KEY_VOLTAGES = "voltages"
KEY_SAMPLING_RATE = "sampling_rate"
KEY_GAIN = "gain"
KEY_START = "start"
KEY_END = "end"
KEY_DTYPE = "dtype"
KEY_SCALE = "scale"

SUPPORTED_DTYPES = ("float32", "int16")

_INT16_MAX = 32767


def save_mea_npz(mea: MEA, path: str, dtype: str = "float32") -> None:
    """MEA計測データを .npz(圧縮)で保存する。

    Parameters
    ----------
    mea : MEA
        保存対象の計測データ
    path : str
        保存先パス(.npz)。拡張子が無ければ numpy が付与する
    dtype : str
        "float32"(実質無損失, 約1/2) / "int16"(16bit量子化, 約1/4)

    Notes
    -----
    時刻行(array[0])は保存しない。読込時に start/SAMPLING_RATE/列数から再生成する。
    int16 は電位を `scale = max(|V|)/32767` で量子化して保存し、復元時に scale を掛ける
    (誤差 < scale の16bit精度で実質無損失)。
    """
    if dtype not in SUPPORTED_DTYPES:
        raise ValueError(
            f"dtypeは {SUPPORTED_DTYPES} のいずれかを指定してください: {dtype}"
        )

    # 時刻行(0行目)は保存せず、電位のみ(1〜64行目)を保存する
    voltages = np.asarray(mea.array[1:], dtype=np.float32)

    if dtype == "int16":
        max_abs = float(np.max(np.abs(voltages))) if voltages.size else 0.0
        scale = max_abs / _INT16_MAX if max_abs > 0 else 1.0
        stored = np.round(voltages / scale).astype(np.int16)
    else:  # float32
        scale = 1.0
        stored = voltages

    np.savez_compressed(
        path,
        **{
            KEY_HED_PATH: str(mea.hed_path.path),
            KEY_VOLTAGES: stored,
            KEY_SAMPLING_RATE: np.int64(mea.SAMPLING_RATE),
            KEY_GAIN: np.int64(mea.GAIN),
            KEY_START: np.float64(mea.start),
            KEY_END: np.float64(mea.end),
            KEY_DTYPE: dtype,
            KEY_SCALE: np.float64(scale),
        },
    )
