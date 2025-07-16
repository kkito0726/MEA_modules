## MEA計測データ解析ライブラリ (PyMEA)

MEA計測データをPython3で読み込んで数値計算やグラフ描画を行うためのライブラリ。複雑な処理を抽象化してよりシンプルなコードでデータ解析を行うことができます。

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

### サンプルコード

- フィルターなし (データをそのまま読み込む)

```python
from pyMEA import *

hed_path = "/User/you/your_record_data.hed"
start, end = 0, 30
electrode_distance = 450

mea = read_MEA(hed_path, start, end, electrode_distance)
```

- フィルターあり

```python
# 移動平均で処理する (神経細胞の計測データでよく使われる)
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.FILTER_MEA)

# 心筋細胞の平均波形を算出する
# 平均波形を計算する範囲を変えたい場合は引数front, backを変更する
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.CARDIO_AVE_WAVE)
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

# フレーム間0.1秒で100フレーム分のGIF動画を作成
fig_images = [
    mea.fig.showAll(
        0 + i * 0.1, 
        1 + i * 0.1, 
        isBuf=True, 
        dpi=100, 
        figsize=(10, 8)
    ) 
    for i in range(68)
]
video = VideoMEA(fig_images)
video.save_gif("./output_64waves.gif", duration = 0.1) # 動画の保存
video.display_gif(duration = 0.1)                      # 動画をjupyter上で再生
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
mea.fig.plotPeaks(ch=2, peak_index, start=0, end=1, volt_min=-300, volt_max=300)
```

### 波形を縦に積み上げて描画

```python
def showDetection(
    self,
    eles: list[int],
    start=None,
    end=None,
    adjust_wave=200,
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

## Article
[K.Kito *et al* (2024) *Biophysics and Physicobiology*, e210026](https://doi.org/10.2142/biophysico.bppb-v21.0026)

## Language
[English](./README.md)
