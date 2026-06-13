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
from pyMEA.infrastructure.read_bio import decode_hed, hed2array


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
    hed_path = HedPath(hed_path)
    hed_data = decode_hed(hed_path)
    array = hed2array(hed_path, start, end)
    data = MEA(hed_path, start, end, hed_data.SAMPLING_RATE, hed_data.GAIN, array)

    if filter_type == FilterType.CARDIO_AVE_WAVE:
        data = cardio_ave_wave_factory(data, front, back, distance)
    elif filter_type == FilterType.FILTER_MEA:
        filtered_array = filter_by_moving_average(data, power_noise_freq, steps)
        data = MEA(
            hed_path, start, end, hed_data.SAMPLING_RATE, hed_data.GAIN, filtered_array
        )
    elif filter_type == FilterType.CARDIO_DENOISE:
        # 心筋(強〜中信号): ドリフト除去 + 共通モードノイズ除去
        data = data.highpass(1).common_median_reference()
    elif filter_type == FilterType.CARDIO_DENOISE_WEAK:
        # 微弱心筋: 帯域通過(広帯域ノイズ除去) + 共通モードノイズ除去
        data = data.bandpass(1, 1000).common_median_reference()
    elif filter_type == FilterType.NEURO_DENOISE:
        # 神経: スパイク帯のみ通過
        data = data.bandpass(100, 3000)
    else:
        pass

    electrode = Electrode(electrode_distance)
    fig = FigMEA(data, electrode)
    calculator = Calculator(data, electrode_distance)

    return PyMEA(data, electrode, fig, calculator)
