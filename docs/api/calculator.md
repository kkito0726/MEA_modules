
## Calculator class

Utilities for calculating ISI, FPD, conduction velocity, and more

```python
from pyMEA import *

hed_path = "/Users/you/your_mea_recording.hed"
start, end = 0, 5

# Read recording data
data = MEA(hed_path, start, end)

# Initialize calculator with electrode distance
electrode_distance = 450 # Distance between electrodes (μm)
cal = Calculator(data, 450)

# Detecting negative peaks in the waveform
peak_index = detect_peak_neg(data)

ch = 32 # electrode number
isi = cal.isi(peak_index, ch) # ISI (s)
fpd = cal.fpd(peak_index, ch) # FPD (s)

# Calculate Conduction velocity between electrodes (m/s)
conduction_velocity = cal.conduction_velocity(peak_index, ch, ch+1)

# Conduction velocity calculated by gradient analysis (m/s)
gradient_velocity = cal.gradient_velocity(peak_index)
```

## Language
[Japanese](./README_ja.md)
