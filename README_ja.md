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
# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
data = MEA(hed_path, start, end)

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
data.info
```

### ６４電極の波形をすべて表示

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
data = MEA(hed_path, start, end) # MEA計測データの読み込み
fm = FigMEA(data) # グラフ描画クラスのインスタンス化
fm.showAll()
```

### 指定の 1 電極表示

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
data = MEA(hed_path, start, end) # MEA計測データの読み込み
fm = FigMEA(data) # グラフ描画クラスのインスタンス化

ch = 1 # 表示したい電極番号
fm.showSingle(ch)
```

### 波形とピーク位置を確認

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
data = MEA(hed_path, start, end) # MEA計測データの読み込み
fm = FigMEA(data) # グラフ描画クラスのインスタンス化

ch = 1 # 表示したい電極番号
peak_index_neg = detect_peak_neg(data, 3000)
peak_index_pos = detect_peak_pos(data, 3000)

# 上下両方のピークをプロットする場合
fm.plotPeaks(ch, peak_index_neg, peak_index_pos)

# 下のピークをプロットする場合
fm.plotPeaks(ch, peak_index_neg)
```

### カラーマップ描画

```python
from pyMEA import *

hed_path = "/Users/you/MEA_record_example.hed"
start, end = 0, 5

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
data = MEA(hed_path, start, end) # MEA計測データの読み込み
fm = FigMEA(data) # グラフ描画クラスのインスタンス化
peak_index = detect_peak_neg(data, 3000)

fm.draw_2d(peak_index, 450)
```
