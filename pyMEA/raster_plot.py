import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray


def raster_plot(
    MEA_data: ndarray,
    peak_index: ndarray,
    eles: list[int],
    tick_ch=1,
    figsize=(8, 8),
    start=0,
    end=120,
) -> None:
    plt.figure(figsize=figsize, dpi=300)
    for i, ele in enumerate(eles):
        plt.plot(
            MEA_data[0][peak_index[ele]],
            np.ones(len(peak_index[ele])) * i,
            "|",
            color="black",
            markersize=4,
        )

    plt.ylim(-1, len(eles) + 1)

    # 縦軸の目盛りを電極番号に変更
    ele_label = np.array([str(eles[i]) for i in range(len(eles))])
    l = np.arange(0, len(eles), tick_ch)
    plt.yticks(l, ele_label[l])

    plt.xlim(start, end)
    plt.xlabel("Time (s)")
    plt.ylabel("Electrode Number")
    plt.tight_layout()
    plt.show()
