from test.utils import get_resource_path

from pyMEA import CardioAveWave, Calculator
from pyMEA.figure.FigMEA import FigMEA
from pyMEA.find_peaks.peak_detection import detect_peak_neg, detect_peak_pos

path = get_resource_path("230615_day2_test_5s_.hed")

start, end = 0, 5
front, back = 0.05, 0.3
data = CardioAveWave(path.__str__(), start, end, front, back)
cal = Calculator(data, 450)
neg_peak_index = detect_peak_neg(data.array)
pos_peak_index = detect_peak_pos(data.array, height=(0, 500))
fm = FigMEA(data)


if __name__ == "__main__":
    print(data.info)
    fpds = cal.fpd(neg_peak_index, 19)
    fpds.show(data)
    fpds.show(data, volt_min=-100, volt_max=100)

    # 64電極表示
    fm.showAll(start, end, dpi=100)

    # 1電極表示
    fm.showSingle(32, 0, front + back)

    # ピーク抽出位置確認
    fm.plotPeaks(32, neg_peak_index, pos_peak_index, volt_min=-2000, volt_max=2000)

    # 波形積み上げ表示
    fm.showDetection([i for i in range(1, 65)], start, end, dpi=100)

    # ラスタプロット
    fm.raster_plot(neg_peak_index, [i for i in range(1, 65)], dpi=100)

    # ヒストグラム作成
    fm.mkHist(neg_peak_index, [i for i in range(1, 65)], dpi=100)

    # 2Dカラーマップ
    grads = fm.draw_2d(neg_peak_index, 450, dpi=100)
    print(grads.r2s)

    # 3Dカラーマップ
    fm.draw_3d(neg_peak_index, 450, dpi=100)
