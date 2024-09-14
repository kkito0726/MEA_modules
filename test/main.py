from pyMEA import *

path = "./public/230615_day2_test_5s_.hed"

start, end = 1, 2
data = MEA(path, start, end)
neg_peak_index = detect_peak_neg(data.array)
pos_peak_index = detect_peak_pos(data.array, height=500)


if __name__ == "__main__":
    data.info

    # 64電極表示
    data.showAll(start, end)

    # 1電極表示
    data.showSingle(32, start, end)

    # ピーク抽出位置確認
    data.plotPeaks(32, neg_peak_index, pos_peak_index, volt_min=-2000, volt_max=2000)

    # 波形積み上げ表示
    data.showDetection([i for i in range(1, 65)], start, end)

    # ラスタプロット
    data.raster_plot(neg_peak_index, [i for i in range(1, 65)])

    # 2Dカラーマップ
    data.draw_2d(neg_peak_index, 450)

    # 3Dカラーマップ
    data.draw_3d(neg_peak_index, 450)
