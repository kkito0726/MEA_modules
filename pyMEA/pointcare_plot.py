import numpy as np
from numpy import ndarray, float64
from sklearn.preprocessing import minmax_scale
import matplotlib.pyplot as plt

# データの正規化
def normalize_data(data: ndarray, range=(-1, 1)) -> ndarray:
  return minmax_scale(data, range)

# 自己相関係数の計算
def autocorrelation(data, k: int) -> float64:
  y_avg = np.mean(data)
  
  # 分子の計算
  sum_of_covariance = 0
  for i in range(k+1, len(data)):
    covariance = ( data[i] - y_avg ) * ( data[i-(k+1)] - y_avg )
    sum_of_covariance += covariance

  # 分母の計算
  sum_of_denominator = 0
  for u in range(len(data)):
    denominator = ( data[u] - y_avg )**2
    sum_of_denominator += denominator

  return sum_of_covariance / sum_of_denominator


# ポワンカレプロット
def pointcare_plot(data, tau):
  fig = plt.figure()
  ax = fig.add_subplot(111)
  delta_data = np.roll(data, tau)
  plt.plot(data, delta_data, color="k")
  ax.set_aspect("equal", adjustable="box")
  plt.xlabel("Normalized EP (t)")
  plt.ylabel("Normalized EP (t+τ)")
  
  plt.show()