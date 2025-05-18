from test.utils import get_resource_path

from pyMEA import Calculator, detect_peak_all
from pyMEA.figure.FigMEA import FigMEA
from pyMEA.figure.plot.plot import circuit_eles
from pyMEA.find_peaks.peak_detection import detect_peak_neg, detect_peak_pos
from pyMEA.read.model.MEA import MEA

path = get_resource_path("230615_day2_test_5s_.hed")

start, end = 1, 2
data = MEA(path.__str__(), start, end)
cal = Calculator(data, 450)
neg_peak_index = detect_peak_neg(data)
pos_peak_index = detect_peak_pos(data, height=(0, 500))
all_peak_index = detect_peak_all(data)
fm = FigMEA(data)
dpi = 100


if __name__ == "__main__":
    print(data.info)
    fpds = cal.fpd(neg_peak_index, 19)
    fpds.show(data)
    fpds.show(data, volt_min=-100, volt_max=100)

    # 64電極表示
    fm.showAll(start, end, dpi=dpi)

    # 1電極表示
    fm.showSingle(32, start, end)

    # ピーク抽出位置確認
    fm.plotPeaks(32, neg_peak_index, pos_peak_index, volt_min=-2000, volt_max=2000)
    fm.plotPeaks(32, all_peak_index, volt_min=-2000, volt_max=2000)

    # AMC経路カラーマップ
    fm.draw_line_conduction(neg_peak_index, 450, circuit_eles, isLoop=True, dpi=dpi)
    fm.draw_line_conduction(
        neg_peak_index, 450, [9, 10, 11, 12, 13, 14, 15, 16], isLoop=False, dpi=dpi
    )
