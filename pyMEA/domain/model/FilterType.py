from enum import IntEnum, auto


class FilterType(IntEnum):
    NONE = auto()  # 計測生データを使用する場合
    CARDIO_AVE_WAVE = auto()  # 心筋細胞の平均波形を使用する場合
    FILTER_MEA = auto()  # 神経用 データの移動平均を取る
    CARDIO_DENOISE = auto()  # 心筋(強〜中信号): highpass(1Hz) + 共通中央値リファレンス
    CARDIO_DENOISE_WEAK = auto()  # 微弱心筋: bandpass(1-1000Hz) + 共通中央値リファレンス
    NEURO_DENOISE = auto()  # 神経: bandpass(100-3000Hz)
