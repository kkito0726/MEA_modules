import io
import itertools

import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray

from pyMEA.find_peaks.peak_model import Peaks64
from pyMEA.read.model.MEA import MEA
from pyMEA.utils.decorators import output_buf


def peak_flatten(MEA_data: MEA, peak_index: Peaks64, eles: list[int]) -> ndarray:
    detect_time = [MEA_data[0][peak_index[i]] for i in eles]
    detect_time = list(itertools.chain.from_iterable(detect_time))

    return np.array(detect_time)


@output_buf
def mkHist(
    MEA_data: MEA,
    peak_index: Peaks64,
    eles: list[int],
    figsize=(20, 6),
    bin_duration=0.05,
    sampling=10000,
    start=0,
    end=120,
    dpi=300,
    isBuf=False,
) -> io.BytesIO | ndarray:
    detect_time = peak_flatten(MEA_data, peak_index, eles)

    plt.figure(figsize=figsize, dpi=dpi)
    bins = len(MEA_data[0]) / sampling / bin_duration
    y, _, _ = plt.hist(detect_time, bins=int(bins), color="k")
    plt.xlim(start, end)
    plt.ylabel("Number of spikes")
    plt.xlabel("Time (s)")

    return y
