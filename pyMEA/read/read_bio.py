import os
from typing import Tuple

import numpy as np
from numpy import ndarray

from pyMEA.read.model.BioPath import BioPath
from pyMEA.read.model.HedPath import HedPath
from pyMEA.utils.decorators import time_validator


# hedファイルの解読関数
def decode_hed(hed_path: HedPath) -> Tuple[int, int]:
    # hedファイルを読み込む。
    hed_data = np.fromfile(hed_path.path, dtype="<h", sep="")

    # rate（サンプリングレート）、gain（ゲイン）の解読辞書。
    rates = {0: 100000, 1: 50000, 2: 25000, 3: 20000, 4: 10000, 5: 5000}
    gains = {
        16436: 20,
        16473: 100,
        16527: 1000,
        16543: 2000,
        16563: 5000,
        16579: 10000,
        16595: 20000,
        16616: 50000,
    }

    # サンプリングレートとゲインを返す。
    # hed_dataの要素16がrate、要素3がgainのキーとなる。
    return rates[int(hed_data[16])], gains[int(hed_data[3])]


# bioファイルを読み込む関数
def read_bio(
    bio_path: BioPath,
    start: int,
    end: int,
    sampling_rate=10000,
    gain=50000,
    volt_range=100,
) -> ndarray:  # sampling_rate (Hz), volt_range (mV)
    electrode_number = 64
    data_unit_length = electrode_number + 4

    bytesize = np.dtype("<h").itemsize
    data = (
        np.fromfile(
            bio_path.path,
            dtype="<h",
            sep="",
            offset=start * sampling_rate * bytesize * data_unit_length,
            count=(end - start) * sampling_rate * data_unit_length,
        )
        * (volt_range / (2**16 - 2))
        * 4
    )
    data = data.reshape(int(len(data) / data_unit_length), data_unit_length).T
    data = np.delete(data, range(4), 0)

    # Gainの値に合わせてデータを増幅させる。
    if gain != 50000:
        amp = 50000 / gain
        data *= amp

    t = np.arange(len(data[0])) / sampling_rate
    t = t.reshape(1, len(t))
    t = t + start
    data = np.append(t, data, axis=0)

    return data


# hedファイルの情報からbioファイルを一気に読み込む
@time_validator
def hed2array(hed_path: HedPath, start: int, end: int) -> ndarray:
    """
    ヘッダーファイルからサンプリングレートとGainを読み取りbioファイルを読み込む\n
    Parameters
    ----------
        hed_path: ヘッダーファイルのパス\n
        start: 読み込み開始時間\n
        end: 読み込み終了時間\n

    Returns
    -------
        [\n
            [時刻データ],\n
            [ch 1の電位データ],\n
            [ch 2の電位データ],\n
            [ch 3の電位データ],\n
            .\n
            .\n
            .\n
            [ch 64の電位データ]\n
        ]
    """
    # hedファイルからサンプリングレートとゲインを取得
    samp, gain = decode_hed(hed_path)

    bio_path = BioPath(os.path.splitext(hed_path.path)[0] + "0001.bio")
    return read_bio(bio_path, start, end, sampling_rate=samp, gain=gain)
