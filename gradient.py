import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import statistics
from electrode_distance import distance

# ピーク抽出できなかったchを除去する。
def remove_undetected_ch(data, peak_index):
  # ピークの時刻 (s)を取得
  time = [data[0][peak_index[i]] for i in range(1, 65)]
  
  # 各電極の取得ピーク数の最頻値以外の電極は削除
  peaks = [len(peak_index[i]) for i in range(1, 65)]
  remove_ch = []
  for i in range(len(time)):
      if len(time[i]) != statistics.mode(peaks):
          remove_ch.append(i)
  print("弾いた電極番号: ", np.array(remove_ch))
  time_del = np.delete(time, remove_ch, 0)
  
  return time_del, remove_ch

# 伝導のカラーマップを描画
def draw(data, peak_index):
  time_del, remove_ch = remove_undetected_ch(data, peak_index)

  # # データ範囲を取得
  x_min, x_max = min(distance[:, 0]), max(distance[:, 0])
  y_min, y_max = min(distance[:, 1]), max(distance[:, 1])

  # 取得したデータ範囲で新しく座標にする配列を作成
  new_x_coord = np.linspace(x_min, x_max, 100)
  new_y_coord = np.linspace(y_min, y_max, 100)

  # ベクトル描画用の座標も作成
  new_x_coord_vec = np.linspace(x_min, x_max, 8)
  new_y_coord_vec = np.linspace(y_min, y_max, 8)

  # x, yのグリッド配列作成
  xx, yy = np.meshgrid(new_x_coord, new_y_coord)
  xx_vec, yy_vec = np.meshgrid(new_x_coord_vec, new_y_coord_vec)
  
  # 既知のx, y座標を取得
  knew_xy_coord = np.delete(distance, remove_ch, 0)
  # l = np.array([0.0, 0.5, 1.0, 1.5, 2.0])

  for f in range(len(time_del[0])):
    knew_values = [time_del[i][f] for i in range(len(time_del))]
    knew_values -= np.min(knew_values)
    # 単位をmsに変換
    knew_values *= 1000

    result = griddata(points=knew_xy_coord, values=knew_values, xi=(xx, yy), method='cubic')
    result -= np.min(result)
    result_vec = griddata(points=knew_xy_coord, values=knew_values, xi=(xx_vec, yy_vec), method='cubic')
    
    # 勾配ベクトルを算出
    grady, gradx = np.gradient(result_vec, 1, 1)
    
    # グラフ表示
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='box')
    c = ax.contourf(xx, yy, result, cmap='jet')
    ax.contour(xx, yy, result,colors="k", linewidths = 0.5, linestyles = 'solid')
    plt.scatter(distance[:, 0], distance[:, 1], marker=",", color="w")
    plt.scatter(knew_xy_coord[:,0], knew_xy_coord[:,1],marker=",", color="gray")
    plt.quiver(xx_vec, yy_vec, gradx , grady)
    plt.colorbar(c)
    plt.show()

# ベクトル解析で伝導速度を算出
def calc_velocity_from_grid(data, peak_index, mesh_num=8):
  time_del, remove_ch = remove_undetected_ch(data, peak_index)

  # データ範囲を取得
  x_min, x_max = min(distance[:, 0]), max(distance[:, 0])
  y_min, y_max = min(distance[:, 1]), max(distance[:, 1])

  # 取得したデータ範囲で新しく座標にする配列を作成
  new_x_coord = np.linspace(x_min, x_max, mesh_num)
  new_y_coord = np.linspace(y_min, y_max, mesh_num)
  xx, yy = np.meshgrid(new_x_coord, new_y_coord)
  
  # 既知のX, Y座標を取得
  knew_xy_coord = np.delete(distance, remove_ch, 0)

  cv_list = []
  for f in range(len(time_del[0])):
    knew_values = [time_del[i][f] for i in range(len(time_del))]
    knew_values -= np.min(knew_values)
    
    # 抜けているデータを既知のデータから補完する
    result = griddata(points=knew_xy_coord, values=knew_values, xi=(xx, yy), method='cubic')
    
    # 勾配ベクトルを算出
    grady, gradx = np.gradient(result, 450*10**-6)

    cv = 1/np.sqrt(gradx**2 + grady**2)
    cv_list.append(cv)
    
  return cv_list
