import sys
sys.path.append("../../MEA-modules")
from read_bio import hed2array
from peak_detection import detect_peak_neg
from plot import showAll
from gradient import draw, calc_velocity_from_grid

hed_path = input("ヘッダファイルのパスを入力: ")
start = int(input("読み込み開始時刻を入力: "))
end = int(input("読み込み終了時刻を入力: "))

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
