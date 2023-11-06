import numpy as np
import itertools
import matplotlib.pyplot as plt

from numpy import ndarray


def peak_flatten(MEA_data: ndarray, peak_index: ndarray, start_ch=1, end_ch=64) -> ndarray:
    detect_time = [MEA_data[0][peak_index[i]] for i in range(start_ch, end_ch + 1)]
    detect_time = list(itertools.chain.from_iterable(detect_time))

    return np.array(detect_time)


def mkHist(
    MEA_data: ndarray,
    peak_index: ndarray,
    start_ch=1,
    end_ch=64,
    figsize=(20, 6),
    bin_duration=0.05,
    sampling=10000,
    start=0,
    end=120,
    dpi=300,
) -> ndarray:
    detect_time = peak_flatten(MEA_data, peak_index, start_ch=start_ch, end_ch=end_ch)

    plt.figure(figsize=figsize, dpi=dpi)
    bins = len(MEA_data[0]) / sampling / bin_duration
    y, _, _ = plt.hist(detect_time, bins=int(bins), color="k")
    plt.xlim(start, end)
    plt.ylabel("Number of spikes")
    plt.xlabel("Time (s)")

    return y
