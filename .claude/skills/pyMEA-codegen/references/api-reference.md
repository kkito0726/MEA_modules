# pyMEA API リファレンス

ソースコードから抽出した完全なAPI情報。SKILL.md本体に記載しきれない詳細パラメータや型情報をここにまとめる。

## 目次

1. [read_MEA 詳細パラメータ](#read_mea-詳細パラメータ)
2. [MEA データモデル](#mea-データモデル)
3. [ピーク検出の型体系](#ピーク検出の型体系)
4. [FigMEA 全メソッドシグネチャ](#figmea-全メソッドシグネチャ)
5. [Calculator 全メソッドシグネチャ](#calculator-全メソッドシグネチャ)
6. [計算結果クラス (AbstractValues)](#計算結果クラス-abstractvalues)
7. [FigImage / VideoMEA](#figimage--videomea)
8. [バースト解析](#バースト解析)
9. [ポワンカレプロット・自己相関](#ポワンカレプロット自己相関)
10. [アーティファクト除去](#アーティファクト除去)
11. [Electrode クラス](#electrode-クラス)

---

## read_MEA 詳細パラメータ

```python
def read_MEA(
    hed_path: str,
    start: int,
    end: int,
    electrode_distance: int,
    filter_type=FilterType.NONE,
    # CardioAveWave用パラメータ (filter_type=FilterType.CARDIO_AVE_WAVE の場合のみ有効)
    front=0.05,       # ピークの前の時間 (s)
    back=0.3,         # ピークの後の時間 (s)
    distance=3000,    # ピーク検出の間隔 (フレーム数)
    # FilterMEA用パラメータ (filter_type=FilterType.FILTER_MEA の場合のみ有効)
    power_noise_freq=50,  # 電源ノイズの周波数 (Hz)
    steps=10,             # 移動平均のステップ数
) -> PyMEA
```

### FilterType 一覧
- `FilterType.NONE` — 生データ（デフォルト）
- `FilterType.CARDIO_AVE_WAVE` — 心筋細胞の平均波形。front/back/distance パラメータで調整可能
- `FilterType.FILTER_MEA` — 神経細胞用の移動平均フィルタ。power_noise_freq/steps で調整可能

---

## MEA データモデル

```python
@dataclass(frozen=True)
class MEA:
    hed_path: HedPath
    start: int | float       # 読み込み開始時間 (s)
    end: int | float         # 読み込み終了時間 (s)
    SAMPLING_RATE: int       # サンプリングレート (Hz)
    GAIN: int                # ゲイン
    array: NDArray[float64]  # 電位データ配列 (65 x フレーム数)
```

### プロパティ
- `mea.data.info` — 読み込み情報をprintして文字列を返す（start, end, time, SAMPLING_RATE, GAIN）
- `mea.data.shape` — array.shape を返す (例: (65, 100000))
- `mea.data.time` — 読み込み時間 = end - start (s)

### アクセスパターン
- `mea.data.array[0]` — 時刻データ (s)
- `mea.data.array[ch]` — 電極chの電位データ (μV), ch=1〜64
- `mea.data[ch]` — `mea.data.array[ch]` のショートカット
- `mea[ch]` — PyMEA経由のショートカット（`mea.data.array[ch]` と同等）
- `mea.data.SAMPLING_RATE` — サンプリングレート

---

## ピーク検出の型体系

```
Peaks (1電極のピーク) ← peak_index: NDArray[int64]
  ├── NegPeaks    (下ピーク)
  └── PosPeaks    (上ピーク)

Peaks64 (64電極分のピーク) ← peaks: dict[int, Peaks]
  ├── NegPeaks64  (detect_peak_neg の戻り値)
  ├── PosPeaks64  (detect_peak_pos の戻り値)
  └── AllPeaks64  (detect_peak_all の戻り値)
```

- `peak_index[ch]` で電極chのピーク配列（ndarray）にアクセス
- ch は 1〜64 の範囲（@ch_validator でバリデーション）

### detect_peak_neg / detect_peak_pos の全パラメータ

```python
def detect_peak_neg(
    MEA_data: MEA,
    distance=3000,       # ピーク間の最小間隔 (フレーム数)
    threshold=3,         # SD倍率の閾値
    min_amp=10,          # 最小振幅の閾値 (μV)
    prominence=None,     # 突起度 (scipy.signal.find_peaks の prominence)
    width=None,          # ピークの幅 (scipy.signal.find_peaks の width)
) -> NegPeaks64
```

### detect_peak_all の全パラメータ

```python
def detect_peak_all(
    MEA_data: MEA,
    threshold: tuple[int, int] = (3, 3),  # (上threshold, 下threshold)
    distance=3000,
    min_amp=(10, 10),   # (上の最小閾値, 下の最小閾値)
    prominence=None,
    width=None,
) -> AllPeaks64
```

---

## FigMEA 全メソッドシグネチャ

### showAll
```python
def showAll(
    self,
    start=None,          # None の場合 data.start
    end=5,               # None の場合 start + 5秒
    volt_min=-200,
    volt_max=200,
    figsize=(8, 8),
    dpi=300,
    color: list[str] | list[list[float]] = None,  # 電極ごとの色リスト
    isBuf=False,
) -> FigImage | None
```

### showSingle
```python
def showSingle(
    self,
    ch: int,
    start: int = None,
    end: int = None,
    volt_min=-200,
    volt_max=200,
    figsize=(8, 2),
    dpi=None,
    xlabel="Time (s)",
    ylabel="Voltage (μV)",
    color: str = None,
    isBuf=False,
) -> FigImage | None
```

### plotPeaks
```python
def plotPeaks(
    self,
    ch: int,
    *peak_indexes: Peaks64,   # 可変長引数: 複数のPeaks64を渡せる
    start: int = None,
    end: int = None,
    volt_min=-200,
    volt_max=200,
    figsize=(8, 2),
    dpi=None,
    xlabel="Time (s)",
    ylabel="Voltage (μV)",
    color: str = None,        # 波形の色
    peak_color: list[str] | list[list[float]] = None,  # ピークマーカーの色
    isBuf=False,
) -> FigImage | None
```

### showDetection
```python
def showDetection(
    self,
    eles: list[int],
    start=None,
    end=None,
    adjust_wave=200,       # 波形を何分の1にして描画するか
    isDisplayCh=True,      # 電極番号をY軸に表示するか
    figsize=(12, 12),
    xlabel="Time (s)",
    ylabel="Electrode Number",
    dpi=300,
    color: list[str] | list[list[float]] = None,
    isBuf=False,
) -> FigImage | None
```

### raster_plot
```python
def raster_plot(
    self,
    peak_index: Peaks64,
    eles: list[int],
    tick_ch=1,             # 目盛り間隔 (電極数単位)
    figsize=(8, 8),
    start=None,
    end=None,
    dpi=300,
    isBuf=False,
) -> FigImage | None
```

### mkHist
```python
def mkHist(
    self,
    peak_index: Peaks64,
    eles: list[int],
    figsize=(20, 6),
    bin_duration=0.05,     # ヒストグラムのビン幅 (s)
    start=None,
    end=None,
    y_max=None,            # Y軸の最大値
    dpi=300,
    isBuf=False,
) -> FigImage | np.ndarray
```

### draw_2d
```python
def draw_2d(
    self,
    peak_index: Peaks64,
    base_ch: int | None = None,  # 基準電極 (拍動周期ごとに分割する場合)
    mesh_num=100,                # メッシュ数 (mesh_num x mesh_num)
    contour=False,               # 等高線表示
    isQuiver=True,               # 速度ベクトル表示
    dpi=300,
    cmap="jet",                  # カラーマップ名
    isBuf=False,
) -> VideoMEA | list[Gradient]
```

### draw_3d
```python
def draw_3d(
    self,
    peak_index: Peaks64,
    mesh_num=100,
    xlabel="X (μm)",
    ylabel="Y (μm)",
    clabel="Δt (ms)",
    dpi=300,
    isBuf=False,
) -> VideoMEA | Gradients
```

### draw_line_conduction
```python
def draw_line_conduction(
    self,
    peak_index: Peaks64,
    amc_chs: list[int],           # AMC電極番号の配列（経路順）
    base_ch: int | None = None,   # 基準電極
    isLoop=True,                  # 経路が環状かどうか
    dpi=300,
    isBuf=False,
) -> VideoMEA | None
```
**注意**: `base_ch` を指定する場合、`amc_chs` に含まれる電極を指定すること。

### plot_spectrum
```python
def plot_spectrum(
    self,
    ch: int,
    max_freq=500,       # 表示する最大周波数 (Hz)
    nperseg=2048,       # Welch法のセグメント長
    figsize=(10, 4),
    dpi=100,
    isBuf=False,
)
```

---

## Calculator 全メソッドシグネチャ

### isi
```python
def isi(self, peak_index: Peaks64, ch: int) -> ISI
```

### fpd
```python
def fpd(
    self,
    neg_peak_index: NegPeaks64,   # detect_peak_neg の結果を渡す
    ch: int,
    peak_range=(30, 110),         # 2ndピークの電位範囲 (μV)
    stroke_time=0.02,             # 1stピーク付近の除外時間 (s)
    fpd_range=(0.1, 0.4),         # 許容するFPDの範囲 (s)
    prominence=None,              # 突起度
    width=None,                   # ピークの幅
) -> FPD
```

### conduction_velocity
```python
def conduction_velocity(
    self,
    peak_index: Peaks64,
    ch1: int,        # 電極1
    ch2: int,        # 電極2
) -> ConductionVelocity
```
**注意**: ch1とch2のピーク数が一致しない場合、ValueErrorが発生する。

### gradient_velocity
```python
def gradient_velocity(
    self,
    peak_index: Peaks64,
    base_ch=None,    # 基準電極（拍動周期ごとに分割する場合）
    mesh_num=8,      # メッシュ数
) -> ndarray       # 伝導速度 (m/s) の配列
```

### distance
```python
def distance(self, ch1: int, ch2: int) -> np.float64
```

---

## 計算結果クラス (AbstractValues)

ISI, FPD, ConductionVelocity はすべて AbstractValues を継承。共通プロパティ:

| プロパティ | 型 | 説明 |
|---|---|---|
| `.values` | np.ndarray | 生のNumPy配列 |
| `.mean` | float | 平均値 |
| `.std` | float | 標準偏差 |
| `.se` | float | 標準誤差 (std / N) |
| `.stv` | float | STV (Short-Term Variability) |
| `.coefficient_of_variation` | float | 変動係数 (%) |

- インデックスアクセス可能: `isi[0]`, `len(isi)`, `for v in isi:`
- 算術演算可能: `isi * 1000` (ms変換)
- 比較演算可能: `isi > 0.5`

### ISI 固有
```python
isi.show(start=None, end=None, volt_min=None, volt_max=None, dpi=None, isBuf=False)
```
波形とピーク位置を描画。

### FPD 固有
```python
fpd.show(start=None, end=None, volt_min=None, volt_max=None, dpi=None, isBuf=False)
```
波形と1st/2ndピーク位置を描画。

---

## FigImage / VideoMEA

### FigImage
`isBuf=True` で描画メソッドを呼ぶと返される画像オブジェクト。

```python
fig_image.display()        # Jupyter上に表示
fig_image.save("out.png")  # ファイル保存 (.png, .jpg, .jpeg 対応)
```

### VideoMEA
複数の FigImage をまとめた動画オブジェクト。

```python
video = VideoMEA(fig_images)
video[0]                    # i番目のFigImage
len(video)                  # フレーム数
video.display_gif(duration=0.1)      # Jupyter上でGIF再生
video.save_gif("out.gif", duration=0.1)  # GIF保存
video.save_mp4("out.mp4", fps=10)    # MP4保存 (libx264コーデック)
```

---

## バースト解析

`pyMEA.find_peaks.burst` モジュール（`from pyMEA import *` ではインポートされない。明示的にインポートが必要）。

```python
from pyMEA.find_peaks.burst import sbf_detection, sbf_single, peak_flatten
```

### 同期バースト発火検出 (64電極)
```python
def sbf_detection(
    data: MEA,
    peak_index: Peaks64,
    max_isi=0.004,           # バースト内の最大ISI (s)
    min_spikes=20,           # バースト判定の最小スパイク数
    min_ibi=0.06,            # バースト間の最小間隔 (s)
    spikes_threshold=3000,   # 最終フィルタのスパイク数閾値
) -> list[list[float]]      # バーストごとの発火時刻リスト
```

### 1電極バースト発火検出
```python
def sbf_single(
    data: MEA,
    peak_index: Peaks64,
    ch: int,
    max_isi=0.175,
    min_spikes=5,
    min_ibi=0.8,
    spikes_threshold=9,
) -> list[list[float]]
```

### ピーク時刻のフラット化
```python
def peak_flatten(data: MEA, peak_index: Peaks64) -> ndarray
```
64電極のピーク時刻を1次元配列にまとめる。

参考文献: Matsuda, N., et al. "Detection of synchronized burst firing..." (2018)

---

## ポワンカレプロット・自己相関

`pyMEA.figure.plot.pointcare_plot` モジュール（明示的インポートが必要）。

```python
from pyMEA.figure.plot.pointcare_plot import pointcare_plot, normalize_data, autocorrelation
```

```python
# データの正規化
normalized = normalize_data(data, range=(-1, 1))

# 自己相関係数の計算
r = autocorrelation(data, k)

# ポワンカレプロット
pointcare_plot(data, tau, dpi=300)
```

---

## アーティファクト除去

`pyMEA.find_peaks.peak_detection` モジュール内（明示的インポートが必要）。

```python
from pyMEA.find_peaks.peak_detection import remove_artifact

# レーザー照射などのアーティファクトを除去
cleaned_data, remove_times = remove_artifact(
    MEA_data,              # mea.data.array (ndarray)
    artifact_peaks,        # アーティファクトのピーク位置 (ndarray)
    front_frame=8500,      # アーティファクト前の除去フレーム数
    end_frame=20000,       # アーティファクト後の除去フレーム数
)
```
**注意**: この関数はarrayを直接変更するミュータブルな操作。使用前にコピーすること。

---

## Electrode クラス

```python
@dataclass(frozen=True)
class Electrode:
    ele_dis: int  # 電極間距離 (μm)
```

### メソッド
```python
# 電極のグリッド配列 (8x8) を取得
xx, yy = mea.electrode.get_electrode_mesh

# 特定電極の座標を取得
x, y = mea.electrode.get_coordinate(ch)
```

### 電極配置
8x8グリッド。電極番号1が左上(0,7)、電極番号64が右下(7,0):
```
 1  2  3  4  5  6  7  8    (row 0, y=7)
 9 10 11 12 13 14 15 16    (row 1, y=6)
17 18 19 20 21 22 23 24    (row 2, y=5)
25 26 27 28 29 30 31 32    (row 3, y=4)
33 34 35 36 37 38 39 40    (row 4, y=3)
41 42 43 44 45 46 47 48    (row 5, y=2)
49 50 51 52 53 54 55 56    (row 6, y=1)
57 58 59 60 61 62 63 64    (row 7, y=0)
```
