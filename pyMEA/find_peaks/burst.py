"""
バースト発火を検知するためのプログラム

参考文献
Matsuda, N., et al.
"Detection of synchronized burst firing in cultured human induced pluripotent stem cell-derived neurons using a 4-step method." 
Biochemical and biophysical research communications 497.2 (2018): 612-618.
"""
import itertools

import numpy as np
from numpy import ndarray


# 64電極のpeak_indexを一次元の配列にまとめる。
def peak_flatten(data: ndarray, peak_index: ndarray) -> ndarray:
    detect_time = [data[0][peak_index[i]] for i in range(1, 65)]
    detect_time = list(itertools.chain.from_iterable(detect_time))

    return np.array(detect_time)


# 同期バースト発火検出
def sbf_detection(
    data: ndarray,
    peak_index: ndarray,
    max_isi=0.004,
    min_spikes=20,
    min_ibi=0.06,
    spikes_threshold=3000,
) -> ndarray:
    spikes = peak_flatten(data, peak_index)
    spikes_length = len(spikes)

    sbfs = []
    sbf = []
    for i in range(spikes_length - 1):
        isi = abs(spikes[i + 1] - spikes[i])
        if isi <= max_isi:
            sbf.append(spikes[i])
            if i == spikes_length - 1:
                sbf.append(spikes[-1])
        else:
            if len(sbf) < min_spikes:
                sbf = []
            else:
                sbfs.append(sbf)
                sbf = []

    step3 = []
    for i in range(len(sbfs) - 1):
        if abs(sbfs[i + 1][0] - sbfs[i][-1]) < min_ibi:
            step3.append(sbfs[i] + sbfs[i + 1])
        else:
            step3.append(sbfs[i])

    step4 = []
    for i in range(len(step3)):
        if len(step3[i]) >= spikes_threshold:
            step4.append(step3[i])

    return step4


# 1電極バースト発火検出
def sbf_single(
    data: ndarray,
    peak_index: ndarray,
    ch: int,
    max_isi=0.175,
    min_spikes=5,
    min_ibi=0.8,
    spikes_threshold=9,
):
    spikes = data[0][peak_index[ch]]
    spikes_length = len(spikes)

    sbfs = []
    sbf = []
    for i in range(spikes_length - 1):
        isi = abs(spikes[i + 1] - spikes[i])
        if isi <= max_isi:
            sbf.append(spikes[i])
            if i == spikes_length - 1:
                sbf.append(spikes[-1])
        else:
            if len(sbf) < min_spikes:
                sbf = []
            else:
                sbfs.append(sbf)
                sbf = []
    print(f"Step1-2: {sbfs}")

    step3 = []
    tmp = []
    for s in range(len(sbfs)):
        if tmp == []:
            for a in range(len(sbfs[s])):
                tmp.append(sbfs[s][a])
        elif sbfs[s][0] - sbfs[s - 1][-1] < min_ibi:
            for b in range(len(sbfs[s])):
                tmp.append(sbfs[s][b])
        else:
            step3.append(tmp)
            tmp = []
            for c in range(len(sbfs[s])):
                tmp.append(sbfs[s][c])
            if s == len(sbfs) - 1:
                step3.append(sbfs[-1])

    print(f"Step3: {step3}")

    step4 = []
    for i in range(len(step3)):
        if len(step3[i]) >= spikes_threshold:
            step4.append(step3[i])
    print(f"Step4: {step4}")

    return step4
