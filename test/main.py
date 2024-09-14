from pyMEA import *

path = "./public/230615_day2_test_5s_.hed"

start, end = 1, 2
data = MEA(path, start, end)
peak_index = detect_peak_neg(data.array)


if __name__ == "__main__":

    data.info
    data.showAll(start, end)
    data.showSingle(32, start, end)
    data.showDetection([i for i in range(1, 65)], start, end)
    data.raster_plot(peak_index, [i for i in range(1, 65)])
    data.draw_2d(peak_index, 450)
    data.draw_3d(peak_index, 450)
