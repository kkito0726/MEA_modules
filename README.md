# MEA_modules
A Python library for analyzing recording data acquired with multi electrode array (MEA) system

## Installation
```bash
pip install git+https://github.com/kkito0726/MEA_modules.git
```

## Package
<pre>
MEA_modules
├──pyMEA
   ├── calculator # Utilities for calculating ISI, FPD, conduction velocity, and more
   ├── figure     # Tools for plotting and visualizing data
   ├── find_peaks # Tools for peak detection in waveform
   ├── gradient   # Gradient analysis and related computations
   ├── read       # Reading MEA recording file
</pre>

## Usage
```python
from pyMEA import  *

hed_path = "/Users/you/your_mea_recording.hed"
start, end = 0, 5

# Read recording data
data = MEA(hed_path, start, end)

# Detecting peaks in the waveform
peak_index_neg = detect_peak_neg(data) # Detect positive peaks
peak_index_pos = detect_peak_pos(data) # Detect negative peaks

# Initialize calculator with electrode distance
electrode_distance = 450 # Distance between electrodes (μm)
cal = Calculator(data, 450)

ch = 3 # electrode number

# Calculate Inter Spike Interval (ISI) (sec)
isi = cal.isi(peak_index_neg, ch)

# Calculate Field Potential Duration (FPD) (sec)
fpd = cal.fpd(peak_index_neg, ch)

# Calculate Conduction velocity between electrodes (m/s)
conduction_velocity = cal.conduction_velocity(peak_index_neg, ch, ch+1)

# Conduction velocity calculated by gradient analysis
gradient_velocity = cal.gradient_velocity(peak_index_neg)

# Visualizing data
fm = FigMEA(data)

# Show 64 waveforms
fm.showAll()

# Draw color maps
gradients = fm.draw_2d(peak_index_neg, electrode_distance)
```
## Article
[K.Kito *et al* (2024) *Biophysics and Physicobiology*, e210026](https://doi.org/10.2142/biophysico.bppb-v21.0026)

## Language
[Japanese](./README_ja.md)
