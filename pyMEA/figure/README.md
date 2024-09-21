## FigMEAクラス

グラフ描画のクラス

```python
from pyMEA import *

path = ".hedファイルのパス"
start, end = 0, 5 # 読み込み時間 (s)
ele_dis = 450 # 電極間距離 (μm)

data = MEA(path, start, end) # MEA計測データの読み込み
fm = FigMEA(data) # グラフ描画クラスのインスタンス化
peak_index = detect_peak_neg(data)

# 64電極波形表示 引数で描画パラメータ管理
fm.showAll()

ch = 32 # 電極番号
fm.showSingle(ch) # 1電極波形表示

# ピーク抽出位置確認
fm.plotPeaks(ch, peak_index)

# 波形積み上げ表示
chs = [i for i in range(1, 65)] # 表示したい電極のリスト (今回は1-64電極すべて)
fm.showDetection(chs)

# ラスタプロット
fm.raster_plot(peak_index, chs)

# ピーク位置のヒストグラム
fm.mkHist(peak_index, chs)

# 2Dカラーマップ描画 (Gradientsクラスを返す)
grads = fm.draw_2d(peak_index, ele_dis)

# 3Dカラーマップ描画 (Gradientsクラスを返す)
grads = fm.draw_3d(peak_index, ele_dis)
```
