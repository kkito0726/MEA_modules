from pyMEA import detect_peak_neg, read_MEA

HEDFILE_PATH = "path/to/your_file.hed"
ELECTRODE_DISTANCE = 450  # 電極間距離 (μm)
START = 0   # 開始時刻 (s)
END = 5     # 終了時刻 (s)
CH = 6      # 対象チャンネル番号

mea = read_MEA(HEDFILE_PATH, start=START, end=END, electrode_distance=ELECTRODE_DISTANCE)

peak_index_neg = detect_peak_neg(mea.data)

isi = mea.calculator.isi(peak_index_neg, ch=CH)

print(f"ch{CH} ISI: {isi.values} (s)")
print(f"ch{CH} 平均ISI: {isi.values.mean():.4f} s")
