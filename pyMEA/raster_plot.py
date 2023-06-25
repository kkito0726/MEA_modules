import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray


def raster_plot(
    MEA_data: ndarray, peak_index: ndarray, figsize=(8, 8), start=0, xtick=30
) -> None:
    plt.figure(figsize=figsize, dpi=300)
    for i in range(1, len(MEA_data)):
        plt.plot(
            MEA_data[0][peak_index[i]],
            np.ones(len(peak_index[i])) * i,
            "|",
            color="black",
            markersize=4,
        )
    # plt.title("Positive peaks & Negative peaks")
    plt.xticks(range(0, int(np.max(MEA_data[0])), xtick))
    plt.xlim(start, int(max(MEA_data[0])) + 1)
    plt.ylim(0, 65)
    plt.yticks(range(4, 65, 4))
    plt.xlabel("Time (s)")
    plt.ylabel("Electrode Number")
    plt.show()
