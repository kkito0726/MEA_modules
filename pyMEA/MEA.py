import numpy as np
import matplotlib.pyplot as plt

from pyMEA.read_bio import decode_hed, hed2array
from pyMEA.plot import showAll
from numpy import ndarray

class MEA:
  def __init__(self, hed_path: str, start: int, end: int) -> None:
    self.hed_path: str = hed_path
    self.start: int = start
    self.end: int = end
    self.time: int = end - start
    sampling_rate, gain = decode_hed(self.hed_path)
    self.SAMPLING_RATE: int = sampling_rate
    self.GAIN: int = gain
    
    self.array: ndarray = hed2array(self.hed_path, self.start, self.end)

  def showAll(self, start=0, end=5, volt_min=-200, volt_max=200, figsize=(8, 8), dpi=300) -> None:
    showAll(self.array, self.SAMPLING_RATE, start, end, volt_min, volt_max, figsize, dpi)
    
  def showSingle(self, ch: int,start=0, end=5, volt_min=-200, volt_max=200, figsize=(8, 2), dpi=300, xlabel="Time (s)", ylabel="Voltage (μV)") -> None:
    start_frame = int(start * self.SAMPLING_RATE)
    end_frame = int(end * self.SAMPLING_RATE)
    
    plt.figure(figsize=figsize, dpi=dpi)
    plt.plot(self.array[0][start_frame:end_frame], self.array[ch][start_frame:end_frame])
    plt.xlim(start, end)
    plt.ylim(volt_min, volt_max)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    plt.show()