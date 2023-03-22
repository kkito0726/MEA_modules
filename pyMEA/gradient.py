import numpy as np
from numpy import ndarray
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import statistics
from typing import Tuple, List

# ピーク抽出できなかったchを除去する。
def remove_undetected_ch(data: ndarray, peak_index: ndarray) -> Tuple[List[ndarray], List[int]]:
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

# 格子データを生成
def get_mesh(ele_dis: int, mesh_num):
  # データ範囲を取得
  x_min, x_max = 0, ele_dis*7
  y_min, y_max = 0, ele_dis*7

  # 取得したデータ範囲で新しく座標にする配列を作成
  x_coord = np.linspace(x_min, x_max, mesh_num)
  y_coord = np.linspace(y_min, y_max, mesh_num)

  # 取得したデータ範囲で新しく座標にする配列を作成
  xx, yy = np.meshgrid(x_coord, y_coord)
  
  return xx, yy

# 伝導のカラーマップを描画
def draw(data: ndarray, peak_index: ndarray, ele_dis=450, mesh_num=100, xlabel="", ylabel="", dpi=300) -> None:
  time_del, remove_ch = remove_undetected_ch(data, peak_index)

  # x, yのグリッド配列作成
  xx, yy = get_mesh(ele_dis, mesh_num)
  xx_vec, yy_vec = get_mesh(ele_dis, 8)
  
  # 電極座標を取得
  ele_point = np.array([[np.ravel(xx_vec)[i], np.ravel(np.flipud(yy_vec))[i]] for i in range(64)])
  
  # 既知のx, y座標を取得
  knew_xy_coord = np.delete(ele_point, remove_ch, 0)

  for f in range(len(time_del[0])):
    knew_values = [time_del[i][f] for i in range(len(time_del))]
    knew_values -= np.min(knew_values)
    # 単位をmsに変換
    knew_values *= 1000

    # 抜けているデータを既知のデータから補完する
    result = griddata(points=knew_xy_coord, values=knew_values, xi=(xx, yy), method='cubic')
    result -= np.min(result)
    result_vec = griddata(points=knew_xy_coord, values=knew_values, xi=(xx_vec, yy_vec), method='cubic')
    
    # 勾配ベクトルを算出
    grady, gradx = np.gradient(result_vec)
    
    # グラフ表示
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='box')
    c = ax.contourf(xx, yy, result, cmap='jet')
    ax.contour(xx, yy, result,colors="k", linewidths = 0.5, linestyles = 'solid')
    plt.scatter(ele_point[:, 0], ele_point[:, 1], marker=",", color="w")
    plt.scatter(knew_xy_coord[:,0], knew_xy_coord[:,1],marker=",", color="gray")
    plt.quiver(xx_vec, yy_vec, gradx , grady)
    plt.colorbar(c)
    plt.xticks(np.arange(0, ele_dis*7+1, ele_dis))
    plt.yticks(np.arange(0, ele_dis*7+1, ele_dis))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

# ベクトル解析で伝導速度を算出
def calc_velocity_from_grid(data: ndarray, peak_index: ndarray, ele_dis=450, mesh_num=8) -> List[ndarray]:
  time_del, remove_ch = remove_undetected_ch(data, peak_index)

  # x, yのグリッド配列作成
  xx, yy = get_mesh(ele_dis, mesh_num)
  xx_ele, yy_ele = get_mesh(ele_dis, 8)
  
  # 電極座標を取得
  ele_point = np.array([[np.ravel(xx_ele)[i], np.ravel(np.flipud(yy_ele))[i]] for i in range(64)])
  
  # 既知のX, Y座標を取得
  knew_xy_coord = np.delete(ele_point, remove_ch, 0)

  cv_list = []
  for f in range(len(time_del[0])):
    knew_values = [time_del[i][f] for i in range(len(time_del))]
    knew_values -= np.min(knew_values)
    
    # 抜けているデータを既知のデータから補完する
    result = griddata(points=knew_xy_coord, values=knew_values, xi=(xx, yy), method='cubic')
    
    # 勾配ベクトルを算出 (第二引数はgrid間の距離 (m))
    grady, gradx = np.gradient(result, ele_dis*7/(mesh_num-1)*10**-6)

    # 伝導速度の算出
    cv = 1/np.sqrt(gradx**2 + grady**2)
    cv_list.append(cv)
    
  return cv_list
