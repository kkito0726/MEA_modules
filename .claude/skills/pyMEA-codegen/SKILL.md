---
name: pyMEA-codegen
description: |
  pyMEAライブラリを使ったMEA計測データ解析コードをJupyter Notebook (.ipynb) 上で生成するスキル。
  心筋細胞・神経細胞の細胞外電位データの読み込み、ピーク検出、波形描画、数値計算（ISI, FPD, 伝導速度）、
  カラーマップ生成、動画作成などのコードを、ユーザーの自然言語の要望から正確に生成する。
  pyMEA、MEA、多点電極アレイ、細胞外電位、心筋、神経、ピーク検出、ISI、FPD、伝導速度、カラーマップ、
  ラスタープロット、ヒストグラム、波形描画などに関する質問やコード生成依頼があった場合に使用すること。
  .hedファイルや.bioファイルの読み込み、電極データの解析に関する質問にも対応する。
---

# pyMEA コード生成スキル

pyMEAライブラリを使った解析コードをJupyter Notebook上で生成するためのガイド。
ユーザーは研究者（プログラミング経験は様々）で、pyMEAはインストール済み。

## 基本原則

1. **`from pyMEA import *` を使う** — これが標準的なimport方法
2. **イミュータブル設計を尊重する** — データ変換は常に新しい変数に代入する
3. **電極番号は1〜64** — `array[0]`は時間データ、`array[1]`〜`array[64]`が電極データ
4. **コメントは日本語で書く** — ユーザーは日本語話者

## アーキテクチャ理解

```
PyMEA (frozen dataclass) — read_MEA() で生成
  ├── data:       MEA        # 電位データ（array[0]=時刻, array[1-64]=電極）
  ├── fig:        FigMEA     # グラフ描画メソッド群
  ├── calculator: Calculator # 数値計算メソッド群
  └── electrode:  Electrode  # 電極位置情報
```

## コード生成テンプレート

### 1. データ読み込み（必ず最初に行う）

```python
from pyMEA import *

# .hedファイルのパスを指定
hed_path = "path/to/your_data.hed"
start, end = 0, 30            # 読み込み期間 (秒)
electrode_distance = 450       # 電極間距離 (μm)

mea = read_MEA(hed_path, start, end, electrode_distance)
```

`.hed`ファイルの読み込みには、同じディレクトリに同名の`.bio`ファイルが必要。ユーザーが指定した`.hed`ファイルに対応する`.bio`ファイルが存在するか不明な場合（特にファイルパスが初めて提示された場合）、コード生成前に`.bio`ファイルの存在を確認し、存在しなければユーザーに報告して対応を確認する。

デフォルトは生データ読み込み（`FilterType.NONE`）。**ユーザーから明示的にフィルター指定があった場合のみ** `filter_type` 引数を追加する:
- `FilterType.CARDIO_AVE_WAVE` — 心筋細胞の平均波形（ユーザーが「平均波形」「ave wave」等を指定した場合）
- `FilterType.FILTER_MEA` — 神経細胞用の移動平均フィルタ（ユーザーが「移動平均」「フィルター」等を指定した場合）

```python
# ユーザーがフィルターを指定した場合のみ使用
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.CARDIO_AVE_WAVE)
mea = read_MEA(hed_path, start, end, electrode_distance, FilterType.FILTER_MEA)
```

### 2. ピーク検出

```python
# 下ピーク検出（心筋細胞で最も一般的）
peak_index = detect_peak_neg(mea.data)

# 上ピーク検出
peak_index_pos = detect_peak_pos(mea.data)

# 上下両方のピーク検出
peak_index_all = detect_peak_all(mea.data)
```

パラメータ調整が必要な場合:
- `distance` — ピーク間の最小間隔（フレーム数、デフォルト3000）
- `threshold` — SD倍率の閾値（デフォルト3）
- `min_amp` — 最小振幅の閾値（μV、デフォルト10）

### 3. グラフ描画

#### 全64電極の波形表示
```python
mea.fig.showAll(start=0, end=1, volt_min=-300, volt_max=300)
```

#### 単一電極の波形表示
```python
mea.fig.showSingle(ch=6, start=0, end=1, volt_min=-300, volt_max=300)
```

#### ピーク位置をプロット
```python
peak_index = detect_peak_neg(mea.data)
mea.fig.plotPeaks(6, peak_index, start=0, end=1)
```

#### 波形の積み上げ表示
```python
eles = [1, 2, 3, 4, 5, 6, 7, 8]  # 表示する電極リスト
mea.fig.showDetection(eles=eles, start=0, end=1)
```

#### ラスタープロット
```python
peak_index = detect_peak_neg(mea.data)
eles = [1, 2, 3, 4, 5, 6, 7, 8]
mea.fig.raster_plot(peak_index=peak_index, eles=eles, start=0, end=5)
```

#### ヒストグラム
```python
peak_index = detect_peak_neg(mea.data)
eles = [1, 2, 3, 4, 5, 6, 7, 8]
mea.fig.mkHist(peak_index=peak_index, eles=eles, start=0, end=5)
```

#### 2Dカラーマップ（興奮伝播の可視化）
```python
peak_index = detect_peak_neg(mea.data)
mea.fig.draw_2d(peak_index=peak_index)

# 等高線表示 + 速度ベクトルなし
mea.fig.draw_2d(peak_index=peak_index, contour=True, isQuiver=False)
```

#### 3Dカラーマップ
```python
peak_index = detect_peak_neg(mea.data)
mea.fig.draw_3d(peak_index=peak_index)
```

#### ライン状ネットワークのカラーマップ
```python
peak_index = detect_peak_neg(mea.data)
amc_chs = [1, 2, 3, 4, 5, 6, 7, 8]  # AMC電極の順番
mea.fig.draw_line_conduction(peak_index=peak_index, amc_chs=amc_chs)
```

### 4. 数値計算

#### ISI（拍動間隔）
```python
peak_index = detect_peak_neg(mea.data)
isi = mea.calculator.isi(peak_index, ch=6)

# 統計値の取得
print(f"平均: {isi.mean:.4f} s")
print(f"標準偏差: {isi.std:.4f} s")
print(f"標準誤差: {isi.se:.4f} s")
print(f"STV: {isi.stv:.4f}")
print(f"変動係数: {isi.coefficient_of_variation:.4f}")

# ISIのグラフ表示
isi.show()
```

#### FPD（細胞外電位継続時間）
```python
peak_index = detect_peak_neg(mea.data)
fpd = mea.calculator.fpd(peak_index, ch=6)

print(f"平均: {fpd.mean:.4f} s")
print(f"標準偏差: {fpd.std:.4f} s")

# FPD算出に使用したピークの確認
fpd.show()
```

#### 伝導速度
```python
peak_index = detect_peak_neg(mea.data)
cv = mea.calculator.conduction_velocity(peak_index, ch1=9, ch2=54)

print(f"平均伝導速度: {cv.mean:.4f} m/s")
```

#### 速度ベクトルからの伝導速度
```python
peak_index = detect_peak_neg(mea.data)
gv = mea.calculator.gradient_velocity(peak_index)
```

#### 電極間距離
```python
dist = mea.calculator.distance(ch1=9, ch2=54)
print(f"電極間距離: {dist:.1f} μm")
```

### 5. データ操作

#### 時間範囲の切り出し
```python
mea_slice = mea.from_slice(0.5, 1.5)  # 0.5〜1.5秒を切り出し
```

#### 拍動周期ごとの分割
```python
peak_index = detect_peak_neg(mea.data)
mea_list = mea.from_beat_cycles(peak_index, base_ch=5)
# mea_list[0], mea_list[1], ... で各拍動周期にアクセス
```

#### 時刻を0始まりにリセット
```python
mea = mea.init_time()
```

#### ダウンサンプリング
```python
mea_down = mea.down_sampling(10)  # 1/10にダウンサンプリング
```

#### ノッチフィルタ（電源ノイズ除去）
```python
mea_filtered = mea.iirnotch_filter(filter_hz=50, Q=30)
```

### 6. 動画作成

#### isBuf=True で画像を取得し、VideoMEA で動画化
```python
# 64電極波形のスライド動画
fig_images = [
    mea.fig.showAll(0 + i * 0.1, 1 + i * 0.1, isBuf=True, dpi=100)
    for i in range(100)
]
video = VideoMEA(fig_images)
video.display_gif(duration=0.1)  # Jupyter上で再生
video.save_gif("output.gif", duration=0.1)  # ファイル保存
```

#### カラーマップの動画（拍動ごとに自動生成）
```python
peak_index = detect_peak_neg(mea.data)
video = mea.fig.draw_2d(peak_index=peak_index, isBuf=True)
video.display_gif(duration=0.1)
video.save_gif("colormap.gif", duration=0.1)
```

### 7. 周波数解析

```python
mea.fig.plot_spectrum(ch=6, max_freq=500)
```

## よくある解析フロー

### 心筋細胞の基本解析
```
データ読み込み → ピーク検出 → ISI/FPD計算 → 波形表示 → カラーマップ
```

### 神経細胞の基本解析
```
データ読み込み(FilterType.FILTER_MEA) → ピーク検出 → ラスタープロット → ヒストグラム
```

### 伝導速度解析
```
データ読み込み → ピーク検出 → conduction_velocity or gradient_velocity → 2Dカラーマップ
```

## コード生成時の注意点

### 曖昧な情報は必ずユーザーに確認する（最重要）

以下の情報がユーザーの指示に含まれていない場合、**勝手にデフォルト値を使わず必ずユーザーに質問する**:
- **電極番号（ch）** — どの電極で解析するか。誤った電極で解析すると結果が無意味になるため、推測しない
- **解析期間（start, end）** — 何秒から何秒までのデータを使うか
- **ファイルパス** — .hedファイルの場所
- **電極間距離** — 実験条件に依存するため確認する
- **電極リスト（eles）** — ラスタープロットやヒストグラム等で使う電極の一覧
- **伝導速度のch1, ch2** — どの電極間で計算するか
- **.bioファイルの存在** — `.hed`ファイルのパスが指定されたら、同じディレクトリに同名の`.bio`ファイルが存在するか確認する。`.bio`ファイルが見つからない場合は、コード生成前にユーザーに「.bioファイルが見つかりませんが、同じディレクトリに配置されていますか？」と確認する

その他、ユーザーの意図が曖昧な場合は常にコードを生成する前に確認する。想定と異なるプログラムが出来上がることを防ぐため、推測よりも質問を優先する。

### その他の注意点

- `isBuf=False`（デフォルト）はJupyter上にグラフを直接表示する — 通常はこれで良い
- 画像を変数に保存したい場合やGIF動画を作る場合は `isBuf=True` を使う
- 計算結果オブジェクト（ISI, FPD, ConductionVelocity）は `.values` で生のNumPy配列にアクセスできる
- `plotPeaks` の `peak_indexes` は可変長引数。複数のPeaks64を渡せる
- 色のカスタマイズは `color` 引数で指定可能（文字列 or RGBAリスト）
