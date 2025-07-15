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

## Article
[K.Kito *et al* (2024) *Biophysics and Physicobiology*, e210026](https://doi.org/10.2142/biophysico.bppb-v21.0026)

## Language
[English](./README.md)
