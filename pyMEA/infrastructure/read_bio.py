import os

import numpy as np
from numpy import float64
from numpy._typing import NDArray

from pyMEA.constants import NUM_ELECTRODES, REFERENCE_GAIN
from pyMEA.domain.model.BioPath import BioPath
from pyMEA.domain.model.HedData import HedData
from pyMEA.domain.model.HedPath import HedPath
from pyMEA.domain.validators import time_validator


# hedファイルの解読関数
def decode_hed(hed_path: HedPath) -> HedData:
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
    return HedData(SAMPLING_RATE=rates[int(hed_data[16])], GAIN=gains[int(hed_data[3])])


# bioファイルを読み込む関数
def read_bio(
    bio_path: BioPath,
    start: int,
    end: int,
    sampling_rate=10000,
    gain=REFERENCE_GAIN,
    volt_range=100,
) -> NDArray[float64]:  # sampling_rate (Hz), volt_range (μV)
    data_unit_length = NUM_ELECTRODES + 4

    bytesize = np.dtype("<h").itemsize

    # 生AD値 (int16) を μV へ換算する。
    # (volt_range / (2**16 - 2)) * 4 は (2 * volt_range) / (2**15 - 1) と厳密に等しく、
    # 「int16の最大値 32767 で正規化し、フルスケールを ±2*volt_range に合わせる」ことを意味する。
    # volt_range=100 なら ±200 μV となり、GAIN=50000 時の測定範囲 (装置マニュアル) と一致する。
    # 計算順は変更しないこと (tools/mea2npz が float64 の演算順ごと再現しているため)。
    data = (
        np.fromfile(
            bio_path.path,
            dtype="<h",
            sep="",
            # offset はバイト単位、count は要素数単位 (np.fromfile の仕様)
            offset=start * sampling_rate * bytesize * data_unit_length,
            count=(end - start) * sampling_rate * data_unit_length,
        )
        * (volt_range / (2**16 - 2))
        * 4
    )
    # (フレーム数, 68) へ整形して転置 → (68, フレーム数)
    data = data.reshape(int(len(data) / data_unit_length), data_unit_length).T
    # 各フレーム先頭の4語 (w0=固定マーカー3970, w1/w2=100kHzタイムスタンプ, w3=0) を除去し
    # 電極64chのみを残す。詳細は docs/api/hed_bio_io.md を参照。
    data = np.delete(data, range(4), 0)

    # Gainの値に合わせてデータを増幅させる。
    # 上の換算は GAIN=50000 (±200 μV) 基準なので、実測GAINの測定範囲 ±200 μV * (50000/gain)
    # に合わせて補正する。GAINが低いほど測定範囲が広く、掛ける係数も大きくなる。
    if gain != REFERENCE_GAIN:
        amp = REFERENCE_GAIN / gain
        data *= amp

    # 時刻データを先頭行に付与する。ハードウェアのタイムスタンプではなく公称サンプリング
    # レートから合成し、start を足して録画開始からの絶対時刻にする。
    t = np.arange(len(data[0])) / sampling_rate
    t = t.reshape(1, len(t))
    t = t + start
    data = np.append(t, data, axis=0)

    return data


# hedファイルの情報からbioファイルを一気に読み込む
@time_validator
def hed2array(hed_path: HedPath, start: int, end: int) -> NDArray[float64]:
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
    hed_data = decode_hed(hed_path)

    bio_path = BioPath(os.path.splitext(hed_path.path)[0] + "0001.bio")
    return read_bio(
        bio_path, start, end, sampling_rate=hed_data.SAMPLING_RATE, gain=hed_data.GAIN
    )
