from peak_detection import detect_peak_neg
import numpy as np
from scipy.signal import savgol_filter, find_peaks

# ISIを算出する関数
def calc_isi(MEA_data, ele):
  # 1st peakを抽出
  peak_index = detect_peak_neg(MEA_data)
  peak_time = MEA_data[0][peak_index[ele]]
  isi = np.diff(peak_time)
  
  return isi

def calc_fpd(MEA_data, ele, window=30, height=(10, 80), sampling_rate=10000):
  # 任意の電極の1st peakを抽出
  peak_neg = detect_peak_neg(MEA_data)[ele]
  data = np.copy(MEA_data[ele])
  
  # 先頭の1st peakより前のデータは0に置き換える
  data[:peak_neg[0]] = 0
  
  # 1st peakの前のデータを0に置き換えて不要なピークを潰す
  for idx in peak_neg:
    data[idx-500:idx] = 0
  
  # データをスムージングしてピーク抽出する
  smooth = savgol_filter(data, window, 0)
  peaks, _ = find_peaks(smooth, height=height)
  
  fpd = (peaks - peak_neg[:len(peaks)]) / sampling_rate
  
  return fpd
