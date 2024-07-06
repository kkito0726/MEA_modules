from pyMEA.read.read_bio import hed2array
from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.plot import showAll
from pyMEA.gradient import draw, calc_velocity_from_grid
import glob

hed_path = glob.glob("./public/*.hed")
start = 0
end = 5

# データの読み込み
data = hed2array(hed_path, start, end)

# ピーク抽出
peak_index = detect_peak_neg(data)

# 波形の表示
showAll(data)

# 伝導のカラーマップを描画
draw(data, peak_index)

# ベクトル解析で伝導速度を算出
cv_list = calc_velocity_from_grid(data, peak_index)
print(cv_list)
