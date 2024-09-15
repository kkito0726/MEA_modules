
## Calculatorクラス



```python
from pyMEA import *

path = ".hedファイルのパス"
start = 0
end = 5

data = MEA(path, start, end)
peak_index = detect_peak_neg(data.array)

ele_dis = 450 # 電極間距離 (μm)
cal = Calculator(data, ele_dis)

ch =32
isi = cal.isi(peak_index, ch) # ISI (s)
fpd = cal.fpd(peak_index, ch) # FPD (s)

# 2つの電極間の伝導速度を計算 (m/s)
conduction_velocity = cal.conduction_velocity(peak_index, 1, 2)

# 速度ベクトルから伝導速度を計算 (m/s)
popts, r2s = data.draw_2d(peak_index, 450)
cvs = cal.gradient_velocity(popts)
```