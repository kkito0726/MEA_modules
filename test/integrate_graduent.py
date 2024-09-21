import matplotlib.pyplot as plt
import numpy as np

from pyMEA import Calculator, FigMEA
from pyMEA.find_peaks.peak_detection import detect_peak_neg
from pyMEA.gradient.Gradients import Gradients
from pyMEA.read.MEA import MEA

if __name__ == "__main__":
    path = "/Users/ken/Documents/dev/MEA_modules/test/public/230615_day2_test_5s_.hed"
    data = MEA(path, 1, 2)
    peak_index = detect_peak_neg(data)

    gradients = Gradients(data, peak_index, mesh_num=8)
    cv_class = gradients.calc_velocity()

    fm = FigMEA(data)
    cal = Calculator(data, 450)
    popts, r2 = fm.draw_2d(peak_index, mesh_num=8, dpi=100)
    cvs = cal.gradient_velocity(peak_index, mesh_num=8)

    print(np.mean(cv_class))
    print(np.mean(cvs))
    for cv in cv_class:
        plt.plot(cv, ".", color="b")

    for cv in cvs:
        plt.plot(cv, color="r")
    plt.show()

    gradients.draw_2d(dpi=100)
