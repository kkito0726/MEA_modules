import statistics
import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray
from typing import Tuple, List
from scipy.optimize import curve_fit
import numpy as np
from numpy import ndarray

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
  
  res = []
  for j in range(len(time_del[0])):
    res.append([time_del[i][j] for i in range(time_del.shape[0])])
  
  return np.array(res), remove_ch

def get_mesh(ele_dis: int, mesh_num: int):
  # データ範囲を取得
  x_min, x_max = 0, ele_dis*7
  y_min, y_max = 0, ele_dis*7

  # 取得したデータ範囲で新しく座標にする配列を作成
  x_coord = np.linspace(x_min, x_max, mesh_num)
  y_coord = np.linspace(y_min, y_max, mesh_num)

  # 取得したデータ範囲で新しく座標にする配列を作成
  xx, yy = np.meshgrid(x_coord, y_coord)
  
  return xx, yy

# この三次関数(2変数)に測定値をフィッティングする。
def model(X, p00, p10, p01, p20, p11, p02, p30, p21, p12, p03):
  x, y = X
  z = p00 + p10*x + p01*y + p20*x**2 + p11*x*y + p02*y**2 + p30*x**3 + p21*x**2*y + p12*x*y**2 + p03*y**3
  return z.ravel()

# フィッティング関数
def fit_data(times: ndarray, remove_ch, ele_dis: int) -> List[ndarray]:
  xx, yy = get_mesh(ele_dis, 8)
  xx = np.delete(xx, remove_ch)
  yy = np.delete(yy, remove_ch)
  
  popts, r2s = [], []
  for time in times:
    popt, pcov = curve_fit(model, [xx, yy], time)
    popts.append(popt)
    
    residuals = time - model([xx, yy], *popt)
    rss = np.sum(residuals**2)
    tss = np.sum((time - np.mean(time))**2)
    r2 = 1 - (rss / tss)
    r2s.append(r2)
    
  return popts, r2s

def remove_fit_data(data: ndarray, peak_index: ndarray, ele_dis: int) -> List[ndarray]:
  # ピーク抽出できなかった電極のデータは除去する
  times, remove_ch = remove_undetected_ch(data, peak_index)
  return fit_data(times, remove_ch, ele_dis)

# 2dカラーマップを描画
def draw_2d(popts: List[ndarray], ele_dis: int, mesh_num: int, xlabel="", ylabel="", dpi=300) -> None:
  # grid配列を生成
  xx, yy = get_mesh(ele_dis, mesh_num)
  ex, ey = get_mesh(ele_dis, 8)
  
  for popt in popts:
    # フィッティングした関数からデータを生成
    z = model([xx, yy], *popt)
    z -= np.min(z)
    z *= 1000
    
    # 電極上の勾配を算出する
    z_ele = model([ex, ey], *popt)
    grady, gradx = np.gradient(z_ele.reshape(8, 8), ele_dis*7/(8-1)*10**-6)
    cx, cy = gradx/(gradx**2 + grady**2), grady/(gradx**2 + grady**2)
    
    # グラフにプロットする
    fig = plt.figure(dpi=dpi)
    ax= fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='box')
    c = ax.contourf(xx, yy, z.reshape(mesh_num, mesh_num), cmap='jet')
    ax.contour(xx, yy, z.reshape(100, 100),colors="k", linewidths=0.5, linestyles='solid')
    plt.scatter(ex, ey, marker=",", color="grey")
    plt.quiver(ex, ey, cx, cy)
    plt.colorbar(c)
    plt.xticks(np.arange(0, ele_dis*7+1, ele_dis))
    plt.yticks(np.arange(0, ele_dis*7+1, ele_dis))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

# 3dカラーマップを描画
def draw_3d(popts, ele_dis, mesh_num, xlabel="", ylabel="", dpi=300) -> None:
  xx, yy = get_mesh(ele_dis, mesh_num)
  
  for popt in popts:
    # フィッティングした関数からデータを生成
    z = model([xx, yy], *popt)
    z -= np.min(z)
    z *= 1000
    
    # グラフにプロットする
    fig = plt.figure(dpi=dpi)
    ax = fig.add_subplot(111, projection='3d')
    c = ax.plot_surface(xx, yy, z.reshape(mesh_num, mesh_num), cmap='jet')
    fig.colorbar(c)
    plt.xticks(np.arange(0, ele_dis*7+1, ele_dis))
    plt.yticks(np.arange(0, ele_dis*7+1, ele_dis))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.show()

# 伝導速度の算出
def calc_velocity(popts: List[float], ele_dis: int, mesh_num=8) -> List[ndarray]:
  xx, yy = get_mesh(ele_dis, mesh_num)
  
  cvs_list = []
  for popt in popts:
    z = model([xx, yy], *popt)
    grady, gradx = np.gradient(z.reshape(mesh_num, mesh_num), np.diff(xx)[0][0]*10**-6)
    cx, cy = gradx/(gradx**2 + grady**2), grady/(gradx**2 + grady**2)
    cvs = np.sqrt(cx**2 + cy**2).ravel()
    cvs_list.append(cvs)
    
  return cvs_list