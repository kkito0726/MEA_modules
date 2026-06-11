"""pyMEA全体で共有する定数。

MEAシステムのハードウェア仕様に由来する値をここに集約する。
"""

# 電極数 (8x8グリッド)。array[0]は時間データ、array[1]〜array[64]が電極データ
NUM_ELECTRODES = 64

# 電極グリッドの一辺のサイズ
ELECTRODE_GRID_SIZE = 8

# ピーク検出時のデフォルトのピーク間隔 (フレーム数)
DEFAULT_PEAK_DISTANCE = 3000

# デフォルトの電極間距離 (μm)
DEFAULT_ELECTRODE_DISTANCE = 450

# 電位換算の基準GAIN値
REFERENCE_GAIN = 50000
