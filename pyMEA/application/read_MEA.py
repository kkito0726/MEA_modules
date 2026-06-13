from pyMEA.domain.service.calculator import Calculator
from pyMEA.constants import DEFAULT_PEAK_DISTANCE
from pyMEA.domain.model.Electrode import Electrode
from pyMEA.presentation.FigMEA import FigMEA
from pyMEA.domain.model.FilterType import FilterType
from pyMEA.application.PyMEA import PyMEA
from pyMEA.domain.service.CardioAveWave import cardio_ave_wave_factory
from pyMEA.domain.service.FilterMEA import filter_by_moving_average
from pyMEA.domain.model.HedPath import HedPath
from pyMEA.domain.model.MEA import MEA
from pyMEA.infrastructure.reader import MEAReadResult, create_reader


def _build_pymea(data: MEA, electrode_distance: int) -> PyMEA:
    """MEAデータから各責務クラスを組み立てて PyMEA を返す。"""
    electrode = Electrode(electrode_distance)
    fig = FigMEA(data, electrode)
    calculator = Calculator(data, electrode_distance)
    return PyMEA(data, electrode, fig, calculator)


def _to_mea(result: MEAReadResult) -> MEA:
    return MEA(
        result.hed_path,
        result.start,
        result.end,
        result.sampling_rate,
        result.gain,
        result.array,
    )


def read_MEA(
    hed_path: str,
    start: int,
    end: int,
    electrode_distance: int,
    filter_type=FilterType.NONE,
    front=0.05,
    back=0.3,
    distance=DEFAULT_PEAK_DISTANCE,
    power_noise_freq=50,
    steps=10,
) -> PyMEA:
    """

    Args:
        hed_path: .hedファイルのパス
        start: 読み込み開始地点 (s)
        end: 読み込み終了地点 (s)
        electrode_distance: 電極間距離 (μm)
        filter_type
        #### 以降はCardioAveWaveを使用する用
        front: ピークの前 (s)
        back: ピークの後 (s)
        distance: ピークを取得するデータ数の間隔
        #### 以降はFilterMEAを使用する用
        power_noise_freq:
        steps:

    Returns:
        PyMEA
    -------

    """
    # .hed以外(.bio等)は専用メッセージで弾く(拡張子バリデーション)
    HedPath(hed_path)
    result = create_reader(hed_path, start=start, end=end).read()
    data = _to_mea(result)

    if filter_type == FilterType.CARDIO_AVE_WAVE:
        data = cardio_ave_wave_factory(data, front, back, distance)
    elif filter_type == FilterType.FILTER_MEA:
        filtered_array = filter_by_moving_average(data, power_noise_freq, steps)
        data = MEA(
            result.hed_path,
            result.start,
            result.end,
            result.sampling_rate,
            result.gain,
            filtered_array,
        )
    else:
        pass

    return _build_pymea(data, electrode_distance)


def read_MEA_npz(path: str, electrode_distance: int) -> PyMEA:
    """save_npz で保存した .npz を読み込み PyMEA を返す。

    Parameters
    ----------
    path : str
        .npz ファイルのパス
    electrode_distance : int
        電極間距離 (μm)

    Returns
    -------
    PyMEA

    Notes
    -----
    サンプリングレート・GAIN・start・end はファイルのメタ情報から復元する。
    時刻行は再生成する。.hed/.bio 読込(read_MEA)とは入口を分けている。
    """
    result = create_reader(path).read()
    return _build_pymea(_to_mea(result), electrode_distance)
