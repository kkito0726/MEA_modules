import matplotlib.pyplot as plt
import numpy as np

from pyMEA.gradient.Solver import Solver


class Gradient:
    def __init__(self, solver: Solver, k=5.0**-9) -> None:
        self.solver = solver
        self.grad_x, self.grad_y = self.grad_model((solver.xx, solver.yy), *solver.popt)
        self.vx, self.vy = self.grad_velocity(k, self.grad_x, self.grad_y)

    def grad_model(self, X, p00, p10, p01, p20, p11, p02, p30, p21, p12, p03):
        x, y = X
        grad_x = (
            p10
            + 2 * p20 * x
            + p11 * y
            + 3 * p30 * x**2
            + 2 * p21 * x * y
            + p12 * y**2
        )
        grad_y = (
            p01
            + p11 * x
            + 2 * p02 * y
            + p21 * x**2
            + 2 * p12 * x * y
            + 3 * p03 * y**2
        )
        return grad_x, grad_y

    def grad_velocity(self, k, grad_x, grad_y):
        return k / grad_x, k / grad_y

    def calc_velocity(self):
        return np.sqrt(self.vx**2 + self.vy**2)

    def draw2d(
        self,
        contour=False,
        isQuiver=True,
        xlabel="X (μm)",
        ylabel="Y (μm)",
        clabel="Δt (ms)",
        dpi=300,
        cmap="jet",
    ) -> None:
        # グラフにプロットする
        fig = plt.figure(dpi=dpi)
        ax = fig.add_subplot(111)
        ax.set_aspect("equal", adjustable="box")
        if contour:
            c = ax.contourf(
                self.solver.xx,
                self.solver.yy,
                self.solver.z.reshape(self.solver.mesh_num, self.solver.mesh_num),
                cmap=cmap,
            )
            ax.contour(
                self.solver.xx,
                self.solver.yy,
                self.solver.z.reshape(100, 100),
                colors="k",
                linewidths=0.5,
                linestyles="solid",
            )
        else:
            c = ax.pcolormesh(
                self.solver.xx,
                self.solver.yy,
                self.solver.z.reshape(self.solver.mesh_num, self.solver.mesh_num),
                cmap=cmap,
            )
        # 電極上に速度ベクトルを描画
        ele_solver = Solver(
            self.solver.time, self.solver.remove_ch, self.solver.ele_dis, 8
        )
        ele_grad_x, ele_grad_y = self.grad_model(
            (ele_solver.xx, ele_solver.yy), *ele_solver.popt
        )
        ele_vx, ele_vy = self.grad_velocity(1, ele_grad_x, ele_grad_y)

        plt.scatter(ele_solver.xx, ele_solver.yy, marker=",", color="grey")
        if isQuiver:
            plt.quiver(ele_solver.xx, ele_solver.yy, ele_vx, ele_vy)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        bar = plt.colorbar(c)
        bar.set_label(clabel)
        plt.xticks(np.arange(0, self.solver.ele_dis * 7 + 1, self.solver.ele_dis))
        plt.yticks(np.arange(0, self.solver.ele_dis * 7 + 1, self.solver.ele_dis))

        plt.show()
