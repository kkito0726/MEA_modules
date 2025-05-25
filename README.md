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
electrode_distance = 450 # Distance between electrodes (μm)

# Read recording data
mea = read_MEA(hed_path, start, end, electrode_distance)

# Detecting peaks in the waveform
peak_index_neg = detect_peak_neg(mea.data) # Detect positive peaks
peak_index_pos = detect_peak_pos(mea.data) # Detect negative peaks

ch = 6 # electrode number

# Calculate Inter Spike Interval (ISI) (sec)
isi = mea.calculator.isi(peak_index_neg, ch)

# Calculate Field Potential Duration (FPD) (sec)
fpd = mea.calculator.fpd(peak_index_neg, ch)

# Calculate Conduction velocity between electrodes (m/s)
conduction_velocity = mea.calculator.conduction_velocity(peak_index_neg, ch, ch+1)

# Conduction velocity calculated by gradient analysis
gradient_velocity = mea.calculator.gradient_velocity(peak_index_neg)

# Show 64 waveforms
mea.fig.showAll()

# Draw color maps
gradients = mea.fig.draw_2d(peak_index_neg)
```
## Article
[K.Kito *et al* (2024) *Biophysics and Physicobiology*, e210026](https://doi.org/10.2142/biophysico.bppb-v21.0026)

## Language
[Japanese](./README_ja.md)
