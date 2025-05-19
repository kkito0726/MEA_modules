# MEA-modules

MEA 計測データの読み込み・解析のためのモジュールをまとめたパッケージです。

## 前提条件

- Python のバージョンは 3.12.0 以上推奨です。
- 必要なライブラリは[requirements.txt](https://github.com/kkito0726/MEA_modules/blob/main/requirements.txt)に記載しています。
- pyMEAのインストール同時に必要なライブラリ群がインストールされます。

## インストール

### Git の環境構築ができている場合 (推奨)

ターミナルで任意の Python 環境下で以下のコマンドを実行を実行してください。

```
$ pip install git+https://github.com/kkito0726/MEA_modules.git
```

### Git をインストールしていない場合

1. 右上の Code ボタンからこのリポジトリを Zip でダウンロードする。
2. Zip ファイルを展開し、生成されたフォルダを terminal で開く。
3. 以下のコマンドを実行する。

```
$ pip install -e .
```

このコマンドで setup.py を探してパッケージの読み込みが開始される。

## アップデート

新しいバージョンにアップデートする場合は一度ライブラリを削除して再度インストールする。

```
$ pip uninstall pyMEA -y
$ pip install git+https://github.com/kkito0726/MEA_modules.git
```

## 使い方

### データの読み込み

- .hed と.bio のファイル名は同じ名前にする。
- .hed と.bio は同じ階層のフォルダに保存しておく。

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5
electrode_distance = 450
# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
mea = read_MEA(hed_path, start, end, electrode_distance) # フィルターかけない場合
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.CARDIO_AVE_WAVE) # 心筋細胞の平均波形
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.FILTER_MEA) # 神経用 移動平均をかける 

'''
データには以下の二次元配列が返る
[
  [時刻データ],
  [ch 1の電位データ],
  [ch 2の電位データ],
  [ch 3の電位データ],
  .
  .
  .
  [ch 64の電位データ]
]
'''
```

### 読み込み情報の確認

```
mea.data.info
```

### ６４電極の波形をすべて表示

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5
electrode_distance = 450

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
mea = read_MEA(hed_path, start, end, electrode_distance) # MEA計測データの読み込み
mea.fig.showAll()
```

### 指定の 1 電極表示

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5
electrode_distance = 450

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
mea = read_MEA(hed_path, start, end, electrode_distance) # MEA計測データの読み込み

ch = 1 # 表示したい電極番号
mea.fig.showSingle(ch)
```

### 波形とピーク位置を確認

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5
electrode_distance = 450

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
mea = read_MEA(hed_path, start, end, electrode_distance) # MEA計測データの読み込み

ch = 1 # 表示したい電極番号
peak_index_neg = detect_peak_neg(mea.data, 3000)
peak_index_pos = detect_peak_pos(mea.data, 3000)

# 上下両方のピークをプロットする場合
mea.fig.plotPeaks(ch, peak_index_neg, peak_index_pos)

# 下のピークをプロットする場合
mea.fig.plotPeaks(ch, peak_index_neg)
```

### カラーマップ描画

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5
electrode_distance = 450

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
mea = read_MEA(hed_path, start, end, electrode_distance) # MEA計測データの読み込み
peak_index = detect_peak_neg(mea.data, 3000)

mea.fig.draw_2d(peak_index)

# AMC経路でのカラーマップ描画
chs = [9, 10, 11, 12, 13, 14, 15, 16] # 経路の電極リスト
mea.fig.draw_line_conduction(peak_index, chs, isLoop=False) # 環状経路の場合isLoop = True
```

## Article
[K.Kito *et al* (2024) *Biophysics and Physicobiology*, e210026](https://doi.org/10.2142/biophysico.bppb-v21.0026)

## Language
[English](./README.md)
