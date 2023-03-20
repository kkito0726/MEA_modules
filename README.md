# MEA-modules

MEA 計測データの読み込み・解析のためのモジュールをまとめたパッケージです。

## 前提条件

- Python のバージョンは 3.5 以上で 3.9.7 以上推奨です。
- 必要なライブラリは[requirements.txt](https://github.com/kkito0726/MEA_modules/blob/main/requirements.txt)に記載しています。
- 以下のライブラリを pip でインストールしておきましょう。
  - numpy
  - pandas
  - matplotlib
  - scipy

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

## 使い方

### データの読み込み

```python
from pyMEA.read_bio import hed2array

# 引数はヘッダーファイルのパス, 読み込み開始時間, 読み込み終了時間
data = hed2array(hed_path, start, end)

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
