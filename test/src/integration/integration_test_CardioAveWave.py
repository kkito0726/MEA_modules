from test.utils import get_resource_path

from pyMEA.core.FilterType import FilterType
from pyMEA.find_peaks.peak_detection import detect_peak_neg, detect_peak_pos
from pyMEA.read.read_MEA import read_MEA

path = get_resource_path("230615_day2_test_5s_.hed")

start, end = 0, 5
front, back = 0.05, 0.3
mea = read_MEA(path.__str__(), start, end, 450, FilterType.CARDIO_AVE_WAVE, front, back)
neg_peak_index = detect_peak_neg(mea.data)
pos_peak_index = detect_peak_pos(mea.data, height=(0, 500))


if __name__ == "__main__":
    print(mea.data.info)
    fpds = mea.calculator.fpd(neg_peak_index, 19)
    fpds.show(mea.data)
    fpds.show(mea.data, volt_min=-100, volt_max=100)

    # 64電極表示
    mea.fig.showAll(start, end, dpi=100)

    # 1電極表示
    mea.fig.showSingle(32, 0, front + back)

    # ピーク抽出位置確認
    mea.fig.plotPeaks(32, neg_peak_index, pos_peak_index, volt_min=-2000, volt_max=2000)

    # 波形積み上げ表示
    mea.fig.showDetection([i for i in range(1, 65)], start, end, dpi=100)

    # ラスタプロット
    mea.fig.raster_plot(neg_peak_index, [i for i in range(1, 65)], dpi=100)

    # ヒストグラム作成
    mea.fig.mkHist(neg_peak_index, [i for i in range(1, 65)], dpi=100)
