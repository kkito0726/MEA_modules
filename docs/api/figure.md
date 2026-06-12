## FigMEA class

Tools for plotting and visualizing data

```python
from pyMEA import *

hed_path = "/Users/you/your_mea_recording.hed"
start, end = 0, 5
ele_dis = 450 # Distance between electrodes (μm)

# Read recording data
data = MEA(hed_path, start, end)
fm = FigMEA(data)

# Detecting negative peaks in the waveform
peak_index = detect_peak_neg(data)

# Show 64 waveforms
fm.showAll()

# Show a waveform
ch = 32 # electrode number
fm.showSingle(ch)

# Plot a waveform ant peaks
fm.plotPeaks(ch, peak_index)

# Show stacked waveforms
chs = [i for i in range(1, 65)] # 表示したい電極のリスト (今回は1-64電極すべて)
fm.showDetection(chs)

# Raster plot
fm.raster_plot(peak_index, chs)

# Histgram by peaks
fm.mkHist(peak_index, chs)

# Draw 2D color maps
grads = fm.draw_2d(peak_index, ele_dis)

# Draw 3D color maps
grads_3d = fm.draw_3d(peak_index, ele_dis)
```

## Language
[Japanese](./README_ja.md)
