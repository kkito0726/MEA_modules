import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray


def raster_plot(
    MEA_data: ndarray, peak_index: ndarray, start_ch=1, end_ch=64, figsize=(8, 8), start=0, end=120, xtick=30
) -> None:
    plt.figure(figsize=figsize, dpi=300)
    for i in range(start_ch, end_ch+1):
        plt.plot(
            MEA_data[0][peak_index[i]],
            np.ones(len(peak_index[i])) * i,
            "|",
            color="black",
            markersize=4,
        )
    # plt.xticks(range(0, int(np.max(MEA_data[0])), xtick))
    plt.xlim(start, end)
    plt.ylim(start_ch-1, end_ch+1)
    plt.yticks(range(start_ch, end_ch+1, 4))
    plt.xlabel("Time (s)")
    plt.ylabel("Electrode Number")
    plt.show()
