from enum import IntEnum, auto


class FilterType(IntEnum):
    NONE = auto()  # 計測生データを使用する場合
    CARDIO_AVE_WAVE = auto()  # 心筋細胞の平均波形を使用する場合
    FILTER_MEA = auto()  # 神経用 データの移動平均を取る
