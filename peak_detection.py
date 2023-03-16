import numpy as np
from scipy.signal import find_peaks
    
# 64電極すべての下ピークを取得
def detect_peak_neg(data, distance=5000, width=None, prominence=None):
    peak_index = np.array([None for _ in range(len(data))])
    for i in range(1, len(data)):
        height = np.std(data[i]) * 3
        detect_peak_index = find_peaks(-data[i], height=height, distance=distance, width=width, prominence=prominence)
        
        peak_index[i] = detect_peak_index[0]
        peak_index[i] = np.sort(peak_index[i])
    peak_index[0] = np.array([])
        
    return peak_index

# 64電極すべての上ピークを取得
def detect_peak_pos(data, distance=10000, width=None, prominence=None, height=(10, 80)):
    peak_index = np.array([None for _ in range(len(data))])
    for i in range(1, len(data)):
        # height = np.std(data[i]) * 3
        detect_peak_index = find_peaks(data[i], height=height, distance=distance, width=width, prominence=prominence)
        
        peak_index[i] = detect_peak_index[0]
        peak_index[i] = np.sort(peak_index[i])
    peak_index[0] = np.array([])
        
    return peak_index