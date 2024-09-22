
## Calculatorクラス

ISI (s), FPD (s), 伝導速度 (m/s), 速度ベクトルによる伝導速度 (m/s)を計算する

```python
from pyMEA import *

path = ".hedファイルのパス"
start, end = 0, 5 # 読み込み時間 (s)
ele_dis = 450 # 電極間距離 (μm)

data = MEA(path, start, end) # MEA計測データの読み込み
cal = Calculator(data, ele_dis) # 数値計算クラスのインスタンス化

peak_index = detect_peak_neg(data.array) # 下ピーク抽出

ch = 32 # 電極番号
isi = cal.isi(peak_index, ch) # ISI (s)
fpd = cal.fpd(peak_index, ch) # FPD (s)

# 2つの電極間の伝導速度を計算 (m/s)
conduction_velocity = cal.conduction_velocity(peak_index, 1, 2)

# 速度ベクトルから伝導速度を計算 (m/s)
cvs = cal.gradient_velocity(peak_index)
```