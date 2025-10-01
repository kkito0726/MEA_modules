## MEA計測データ解析ライブラリ (PyMEA)

MEA計測データをPython3で読み込んで数値計算やグラフ描画を行うためのライブラリ。複雑な処理を抽象化してよりシンプルなコードでデータ解析を行うことができます。

## 目次
*   [環境構築](#環境構築)
*   [クラスの関係](#クラスの関係)
*   [import文](#import文)
*   [MEA計測データの読み込み](#mea計測データの読み込み)
    *   [フィルターなし (データをそのまま読み込む)](#フィルターなし-データをそのまま読み込む)
    *   [フィルターあり](#フィルターあり)
    *   [データの分割](#データの分割)
    *   [時刻データの先頭を0始まりにする](#時刻データの先頭を0始まりにする)
    *   [電位データのダウンサンプリング](#電位データのダウンサンプリング)
*   [ピーク抽出](#ピーク抽出)
*   [グラフ描画](#グラフ描画)
    *   [64電極波形描画](#64電極波形描画)
    *   [1電極波形描画](#1電極波形描画)
    *   [ピークをプロット](#ピークをプロット)
    *   [波形を縦に積み上げて描画](#波形を縦に積み上げて描画)
    *   [ラスタープロット](#ラスタープロット)
    *   [ヒストグラム](#ヒストグラム)
    *   [2Dカラーマップ描画](#2dカラーマップ描画)
    *   [3Dカラーマップ描画](#3dカラーマップ描画)
    *   [ライン状心筋細胞ネットワークのカラーマップ描画](#ライン状心筋細胞ネットワークのカラーマップ描画)
*   [動画作成](#動画作成)
*   [数値計算](#数値計算)
    *   [ISI (拍動間隔) の計算](#isi-拍動間隔-の計算)
    *   [FPD (細胞外電位継続時間) の計算](#fpd-細胞外電位継続時間-の計算)
    *   [伝導速度の計算](#伝導速度の計算)
    *   [電極間距離の計算 (直線距離を計算)](#電極間距離の計算-直線距離を計算)
    *   [速度ベクトルから伝導速度を計算](#速度ベクトルから伝導速度を計算)
*   [Article](#article)
*   [Language](#language)

---


## 環境構築

1. [Gitのインストール](https://qiita.com/takeru-hirai/items/4fbe6593d42f9a844b1c)
2. [Python3のインストール](https://www.python.org/downloads/) (3.12.0以上)
3. PyMEAのインストール
以下のコマンドをGit bash上で実行する (必要なライブラリは自動でインストールされる)

```bash
pip install git+https://github.com/kkito0726/MEA_modules.git
```

アップデートする場合は以下のコマンドを実行する

```bash
pip uninstall pyMEA -y
pip install git+https://github.com/kkito0726/MEA_modules.git
```

---

## クラスの関係

このライブラリはPyMEAクラスのインスタンスを作成してグラフ描画や数値計算を行う。業務領域事にクラスを分割してそれぞれのインスタンスをPyMEAクラスが保持する。

```bash
PyMEA
   ├── data:       MEA        # 計測データを保持するクラス (電位データ, GAIN, サンプリングレート)
   ├── fig:        FigMEA     # グラフ描画の責務
   ├── calculator: Calculator # 数値計算の責務 (ISI, FPD, Conduction Velocity, etc)
   ├── electrode:  Electrode  # 電極の位置情報を保持するクラス
```

---

## import文

```python
from pyMEA import *
```

デフォルトimportでは[pyMEA/__init__.py](https://github.com/kkito0726/MEA_modules/blob/main/pyMEA/__init__.py)のオブジェクト (クラス, 関数など)がすべて読み込まれる。これ以外のオブジェクトをimportしたい場合はリポジトリを確認してimport文を記述する。

---

## MEA計測データの読み込み

```python
def read_MEA(
    hed_path: str,               # .hedファイルのパス
    start: int,                  # 読み込み開始時間 (s)
    end: int,                    # 読み込み終了時間 (s)
    electrode_distance: int,     # 電極間距離 (μm)
    filter_type=FilterType.NONE, # フィルタータイプデフォルトでフィルターなし
) -> PyMEA
```

### フィルターなし (データをそのまま読み込む)

```python
# サンプルコード
from pyMEA import *

hed_path = "/User/you/your_record_data.hed"
start, end = 0, 30
electrode_distance = 450

mea = read_MEA(hed_path, start, end, electrode_distance)
```

### フィルターあり
```python
# 移動平均で処理する (神経細胞の計測データでよく使われる)
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.FILTER_MEA)

# 心筋細胞の平均波形を算出する
# 平均波形を計算する範囲を変えたい場合は引数front, backを変更する
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.CARDIO_AVE_WAVE)
```

### データの分割
```python
# 読み込んだデータを任意の期間切り出す
# read_MEAでは読み込み期間を整数でしか指定できないがここでは少数も可能
mea_slice = mea.from_slice(0.25, 0.5)

# 拍動周期ごとにデータを切り出す
# 例: ch 5を基準電極とする
peak_index_neg = detect_peak_neg(mea.data)
mea_list = mea.from_beat_cycles(peak_index_neg, base_ch=5)
```

### 時刻データの先頭を0始まりにする
```python
# 途中から読み込んだデータでグラフ描画するときに時刻データを0始まりにしたい時
mea = mea.init_time()
```

### 電位データのダウンサンプリング
```python
# 1/10にダウンサンプリングする
dawn_sampled_mea = mea.down_sampling(10)
```
---
## ピーク抽出
- 下ピーク抽出, 上ピーク抽出, 上下ピーク抽出を行うメソッドをそれぞれ用意している
- デフォルトimportに対応している
```python
def detect_peak_neg(
    MEA_data: MEA,
    distance=3000, # ピークを取る間隔
    threshold=3,   # SD * thresholdより大きいピークを取る 
    min_amp=10,    # 最小のピークの閾値電位
) -> NegPeaks64:

def detect_peak_pos(
    MEA_data: MEA,
    distance=3000, # ピークを取る間隔
    threshold=3,   # SD * thresholdより大きいピークを取る 
    min_amp=10,    # 最小のピークの閾値電位
) -> PosPeaks64:

def detect_peak_all(
    MEA_data: MEA,
    threshold: tuple[int, int] = (3, 3), # (上, 下)
    distance=3000, # SD * thresholdより大きいピークを取る
    min_amp=(10, 10), # (上, 下)
    width=None,
    prominence=None,
) -> AllPeaks64:
```
```python
# サンプルコード
peak_index_neg = detect_peak_neg(mea.data)
peak_index_pos = detect_peak_pos(mea.data, threshold=2)
peak_index_all = detect_peak_all(mea.data, distance=5000, threshold=(2, 5))

# ch 5のピーク時刻 (s)を求める
time = mea.data[0][peak_index_neg[5]]
```
---
## グラフ描画

### 64電極波形描画

```python
def showAll(
        self,
        start=None,     # 描画開始時間 (s)
        end=5,          # 描画終了時間 (s)
        volt_min=-200,  # 最大電位 (μV)
        volt_max=200,   # 最小電位 (μV)
        figsize=(8, 8), # グラフの縦横比
        dpi=300,        # 解像度
        isBuf=False,    # グラフ画像のインスタンスを返すかどうか (Falseでグラフをjupyter上に表示)
    ) -> FigImage | None:
```
```python   
# サンプルコード
start, end = 0, 1
volt_min, volt_max = -300, 300
mea.fig.showAll(start, end, volt_min, volt_max)
```

### 1電極波形描画

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
    isBuf=False,
) -> FigImage | None:
```
```python
# サンプルコード
mea.fig.showSingle(ch=2, start=0, end=1, volt_min=-300, volt_max=300)
```

### ピークをプロット

```python
def plotPeaks(
    self,
    ch: int,
    *peak_indexes: Peaks64,
    start: int = None,
    end: int = None,
    volt_min=-200,
    volt_max=200,
    figsize=(8, 2),
    dpi=None,
    xlabel="Time (s)",
    ylabel="Voltage (μV)",
    isBuf=False
) -> FigImage | None:
```
```python
# サンプルコード
# ピーク検出
peak_index = detect_peak_neg(mea.data)

# ピークをプロット
ch = 2
mea.fig.plotPeaks(ch, peak_index, start=0, end=1, volt_min=-300, volt_max=300)
```

### 波形を縦に積み上げて描画

```python
def showDetection(
    self,
    eles: list[int],
    start=None,
    end=None,
    adjust_wave=200,
    isDisplayCh = True, # 電極番号をY軸の目盛りに設定
    figsize=(12, 12),
    xlabel="Time (s)",
    ylabel="Electrode Number",
    dpi=300,
    isBuf=False,
) -> FigImage | None:
```
```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
eles = [1, 2, 3, 4, 5] # 描画したい電極をリストに格納
mea.fig.showDetection(eles=eles, start=0, end=1)

# インデックス番号をY軸の目盛りにする (1, 2, 3....)
mea.fig.showDetection(eles=eles, start=0, end=1, isDisplayCh = False)
```

### ラスタープロット

```python
def raster_plot(
    self,
    peak_index: Peaks64,
    eles: list[int],
    tick_ch=1,
    figsize=(8, 8),
    start=None,
    end=None,
    dpi=300,
    isBuf=False,
) -> FigImage | None:
```
```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
eles = [1, 2, 3, 4, 5] # プロットしたい電極をリストに格納
mea.fig.raster_plot(peak_index=peak_index, eles=eles, start=0, end=1)
```
### ヒストグラム

```python
def mkHist(
    self,
    peak_index: Peaks64,
    eles: list[int],
    figsize=(20, 6),
    bin_duration=0.05,
    start=None,
    end=None,
    y_max=None,
    dpi=300,
    isBuf=False,
) -> FigImage | ndarray:
```
```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
eles = [1, 2, 3, 4, 5] # プロットしたい電極をリストに格納
mea.fig.mkHist(peak_index=peak_index, eles=eles, start=0, end=1)
```
### 2Dカラーマップ描画

```python
def draw_2d(
    self,
    peak_index: Peaks64,
    base_ch: int | None = None,
    mesh_num=100,  # mesh_num x mesh_numでデータを生成
    contour=False,  # 等高線で表示するかどうか
    isQuiver=True,  # 速度ベクトルを表示するかどうか
    dpi=300,
    cmap="jet",
    isBuf=False,
) -> VideoMEA | list[Gradient]:
```

```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
mea.fig.draw_2d(peak_index=peak_index)
```

### 3Dカラーマップ描画

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
) -> VideoMEA | Gradients:
```

```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
mea.fig.draw_3d(peak_index=peak_index)
```
### ライン状心筋細胞ネットワークのカラーマップ描画

```python
def draw_line_conduction(
    self,
    peak_index: Peaks64,
    amc_chs: list[int],
    base_ch: int | None = None,
    isLoop=True,
    dpi=300,
    isBuf=False,
) -> VideoMEA | None:
```
```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
amc_chs = [1, 2, 3, 4, 5, 6, 7, 8] # AMCの電極番号
mea.fig.draw_line_conduction(peak_index=peak_index, amc_chs=amc_chs)

# 環状の経路の場合
from pyMEA.figure.plot.plot import circuit_eles

mea.fig.draw_line_conduction(peak_index=peak_index, amc_chs=circuit_eles, isLoop=True)
```

## 動画作成
グラフ描画のメソッドの引数にはisBufという引数があり、これをTrueにするとFigImageクラスのインスタンスが返る。このクラスはグラフ画像情報を保持するクラスであり、このインスタンスのリストをVideoMEAクラスに渡すことでGIF動画の再生や保存ができるようになる。カラーマップ描画系のメソッドは入力したデータのすべての拍動周期に対してグラフ描画するので、isBufをTrueにするとVideoMEAのインスタンスが返るようにしている。
```python
# フレーム間0.1秒で100フレーム分のGIF動画作成
# ここではshowAllメソッドを例に上げる
fig_images = [
    mea.fig.showAll(
        0 + i * 0.1, 
        1 + i * 0.1, 
        isBuf=True, 
        dpi=100, 
        figsize=(10, 8)
    ) 
    for i in range(100)
]
video = VideoMEA(fig_images)
video.save_gif("./output_64waves.gif", duration = 0.1) # 動画の保存
video.display_gif(duration = 0.1)                      # 動画をjupyter上で再生

# カラーマップのGIF動画作成
video = mea.fig.draw_2d(peak_index=peak_index, isBuf=True)
video.save_gif("./output_2d_color_maps.gif", duration = 0.1) # 動画の保存
video.display_gif(duration = 0.1)                      # 動画をjupyter上で再生
```

## 数値計算

### ISI (拍動間隔) の計算

```python
def isi(self, peak_index: Peaks64, ch) -> ISI:
```
```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
isi = mea.calculator.isi(peak_index, ch=2)
isi_stv = isi.stv # ISIのSTV (Short-Term Variability)を計算
isi_cv = isi.coefficient_of_variation # ISIのCV (変動係数, Coefficient of Variation)を計算
```

### FPD (細胞外電位継続時間) の計算

```python
def fpd(
    self,
    neg_peak_index: NegPeaks64,
    ch: int,
    peak_range=(30, 110), # 2ndピークの電位範囲
    stroke_time=0.02,     # 1stピークのストロークの期間 (s)
    fpd_range=(0.1, 0.4), # FPDとして採用する範囲
    prominence=None, # find_peaksのパラメータ
    width=None, # find_peaksのパラメータ
) -> FPD:
```
```python
# サンプルコード
# ch 2のFPD (s)を算出する
peak_index = detect_peak_neg(mea.data)
fpd = mea.calculator.fpd(peak_index, ch=2)
fpd_stv = fpd.stv # FPDのSTV (Short-Term Variability)を計算
fpd_cv = fpd.coefficient_of_variation # ISIのCV (変動係数, Coefficient of Variation)を計算

# FPD算出のために抽出したピークの位置を確認する
fpd.show(mea.data)
```

### 伝導速度の計算

```python
def conduction_velocity(self, peak_index: Peaks64, ch1: int, ch2: int) -> ndarray:
```

```python
# サンプルコード
# ch 9とch 54間の伝導速度を算出する
peak_index = detect_peak_neg(mea.data)
conduction_velocity = mea.calculator.conduction_velocity(peak_index, ch1=9, ch2=54)
```

### 電極間距離の計算 (直線距離を計算)

```python
def distance(self, ch1: int, ch2: int) -> np.float64:
```

```python
# サンプルコード
# ch 9とch 54の直線距離を算出する
distance = mea.calculator.distance(ch1=9, ch2=54)
```

### 速度ベクトルから伝導速度を計算

```python
def gradient_velocity(self, peak_index: Peaks64, base_ch=None, mesh_num=8):
```

```python
# サンプルコード
peak_index = detect_peak_neg(mea.data)
gradient_velocity = mea.calculator.gradient_velocity(peak_index)
```

## Article
[K.Kito *et al* (2024) *Biophysics and Physicobiology*, e210026](https://doi.org/10.2142/biophysico.bppb-v21.0026)

## Language
[English](./README.md)