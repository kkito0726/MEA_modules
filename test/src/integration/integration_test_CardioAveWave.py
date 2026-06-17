from test.fixtures import fixture_hed_path, install_fixture_io

from pyMEA.domain.model.FilterType import FilterType
from pyMEA.domain.service.peak_detection import detect_peak_neg, detect_peak_pos
from pyMEA.application.read_MEA import read_MEA

# リポジトリ管理のフィクスチャ(.npz, 3秒)からデータを供給する
install_fixture_io()
path = fixture_hed_path("cardio")

start, end = 0, 3
front, back = 0.05, 0.3
mea = read_MEA(path.__str__(), start, end, 450, FilterType.CARDIO_AVE_WAVE, front, back)
neg_peak_index = detect_peak_neg(mea.data)
pos_peak_index = detect_peak_pos(mea.data)


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
