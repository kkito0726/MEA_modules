---
marp: true
theme: default
paginate: true
size: 16:9
footer: pyMEA コードガイド
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700;800&display=swap');

:root {
  --bg:        #f4f7fb;   /* 明るいクールなブルーグレー */
  --bg-soft:   #ffffff;
  --fg:        #1f2a37;   /* 濃いスレートグレー（読みやすい） */
  --fg-mute:   #5b6b7c;
  --primary:   #2f6df6;   /* シャープなブルー */
  --accent:    #06b6d4;   /* クールなシアン */
  --code-bg:   #0e1726;   /* ダークコード（白地との対比でキレを出す） */
  --code-fg:   #e6edf6;
  --code-line: #25324a;
  --border:    #d8e1ec;
  --tip-bg:    #ecfbfb;
  --tip-br:    #06b6d4;
  --note-bg:   #eef3ff;
  --note-br:   #2f6df6;
  --font-default: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
  --font-code: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

section {
  background-color: var(--bg);
  background-image:
    radial-gradient(circle at 0% 0%, rgba(47,109,246,0.06), transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(6,182,212,0.06), transparent 38%);
  color: var(--fg);
  font-family: var(--font-default);
  font-weight: 400;
  box-sizing: border-box;
  position: relative;
  line-height: 1.65;
  font-size: 20px;
  padding: 54px 60px;
  border-top: 6px solid var(--primary);
}

/* 見出し */
h1, h2, h3, h4, h5, h6 {
  font-weight: 800;
  color: var(--primary);
  margin: 0;
  padding: 0;
  font-family: var(--font-code);
  letter-spacing: -0.01em;
}

h1 { font-size: 52px; line-height: 1.25; text-align: left; }
h1::before { content: '# '; color: var(--accent); }

h2 {
  font-size: 34px;
  margin-bottom: 26px;
  padding-bottom: 12px;
  border-bottom: 3px solid var(--primary);
  display: inline-block;
}
h2::before { content: '## '; color: var(--accent); }

h3 { color: var(--fg); font-size: 23px; margin-top: 22px; margin-bottom: 8px; }
h3::before { content: '> '; color: var(--accent); font-weight: 800; }

ul, ol { padding-left: 30px; }
li { margin-bottom: 7px; }
li::marker { color: var(--accent); }

/* コードブロック（ダークで引き締める） */
pre {
  background-color: var(--code-bg);
  border: 1px solid var(--code-line);
  border-radius: 10px;
  padding: 16px 20px;
  font-family: var(--font-code);
  font-size: 15px;
  line-height: 1.6;
  box-shadow: 0 8px 24px rgba(15,30,60,0.12);
}

/* インライン code（明るい背景） */
code {
  background-color: #e4ecf8;
  color: #1746a2;
  padding: 2px 7px;
  border-radius: 5px;
  font-family: var(--font-code);
  font-size: 0.88em;
  font-weight: 500;
}

pre code {
  background-color: transparent;
  padding: 0;
  color: var(--code-fg);
  font-weight: 400;
}

strong { color: var(--primary); font-weight: 700; }

/* テーブル */
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 18px;
  margin-top: 6px;
  background: var(--bg-soft);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(15,30,60,0.08);
}
th {
  background: var(--primary);
  color: #fff;
  font-family: var(--font-code);
  font-weight: 700;
  padding: 10px 16px;
  text-align: left;
}
td {
  padding: 9px 16px;
  border-bottom: 1px solid var(--border);
}
tr:last-child td { border-bottom: none; }
tbody tr:nth-child(even) { background: #f6f9fd; }

/* フッター・ページ番号 */
footer {
  font-size: 13px;
  color: var(--fg-mute);
  font-family: var(--font-code);
  position: absolute;
  left: 60px;
  right: 60px;
  bottom: 26px;
  text-align: right;
}
footer::before { content: '// '; color: var(--accent); }
section::after { color: var(--fg-mute); font-family: var(--font-code); font-weight: 700; }

/* リード（表紙・章扉） */
section.lead {
  background: linear-gradient(135deg, #1a2a52 0%, #11407a 55%, #0a6e8c 100%);
  border-top: 6px solid var(--accent);
  display: flex;
  flex-direction: column;
  justify-content: center;
}
section.lead h1 { color: #ffffff; margin-bottom: 20px; }
section.lead h1::before { color: #5fe3ff; }
section.lead p {
  font-size: 22px;
  color: #cfe3f7;
  font-family: var(--font-code);
}
section.lead strong { color: #5fe3ff; }
section.lead::after { color: rgba(255,255,255,0.5); }

/* 解説ボックス：ポイント（シアン） */
.tip {
  background: var(--tip-bg);
  border-left: 5px solid var(--tip-br);
  border-radius: 0 8px 8px 0;
  padding: 11px 18px;
  margin-top: 16px;
  font-size: 18px;
  color: #155e75;
}
.tip strong { color: #0e7490; }

/* 解説ボックス：補足メモ（ブルー） */
.note {
  background: var(--note-bg);
  border-left: 5px solid var(--note-br);
  border-radius: 0 8px 8px 0;
  padding: 11px 18px;
  margin-top: 16px;
  font-size: 18px;
  color: #1e3a8a;
}
.note strong { color: #1d4ed8; }

.lead-sub { color: #9fc4ec !important; font-size: 18px !important; margin-top: 8px; }
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

# pyMEA コードガイド

MEA計測データ解析を、コピペで始める

<span class="lead-sub">初心者向け — 読み込み・ピーク検出・描画・数値計算の基本パターン</span>

---

## このガイドのゴール

pyMEA は **MEA（多点電極アレイ）** で計測した心筋・神経細胞の電位データを解析するライブラリです。

- 専門のプログラミング知識がなくても**コピペで動かせる**
- データ読み込み → 解析 → グラフ化を**一連の流れ**で習得
- まずは「**こう書けば動く**」を体で覚えるのが近道

<div class="note">

**読み方のコツ**：各スライドのコードはそのまま実行できます。ファイルのパスだけ自分のものに書き換えて試してみましょう。

</div>

---

## アジェンダ

| 章 | 内容 |
|----|------|
| 1 | インストール |
| 2 | データの読み込み・保存（.npz） |
| 3 | ピーク抽出 |
| 4 | グラフ描画 |
| 5 | 動画作成 |
| 6 | 数値計算（ISI / FPD / 伝導速度） |

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 1. インストール

最初の一歩。環境を整えよう

---

## インストール

ターミナル（Windows は **Git Bash**）で1行打つだけ。

```bash
pip install git+https://github.com/kkito0726/MEA_modules.git
```

最新版へアップデートする場合：

```bash
pip uninstall pyMEA -y
pip install git+https://github.com/kkito0726/MEA_modules.git
```

<div class="tip">

**ポイント**：`pip` は Python のライブラリを入れる道具です。**Python 3.12** での利用を推奨します。

</div>

---

## クラス構造を理解する

pyMEA では `PyMEA` という1つのオブジェクトが**すべての機能への入口**になります。

```text
PyMEA
  ├── .data        # 計測データ（電位・時間）
  ├── .fig         # グラフ描画
  ├── .calculator  # 数値計算（ISI / FPD / 伝導速度）
  └── .electrode   # 電極位置情報
```

<div class="note">

**初心者向け解説**：`mea.fig.showAll()` のように **ドット（`.`）でたどる** だけで目的の機能に届きます。「`mea` の中の `fig`（描画）の `showAll`（全表示）」と読めばOKです。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 2. データの読み込み

解析はデータを読むところから

---

## import 文

ファイルの先頭に、おまじないを1行書きます。

```python
from pyMEA import *
```

- `*`（アスタリスク）は「**必要なものを全部まとめて読み込む**」という意味
- これ1行で `read_MEA`・`detect_peak_neg` などがすべて使えるようになる

<div class="tip">

**ポイント**：まずはこの1行。何を import するか迷う必要はありません。

</div>

---

## 基本の読み込み

`read_MEA()` に **4つの情報** を渡すだけでデータが読めます。

```python
from pyMEA import *

hed_path = "/Users/you/data.hed"  # ① 計測ファイルのパス
start, end = 0, 30                # ② 読み込む範囲（秒）
electrode_distance = 450          # ③ 電極間の距離（μm）

mea = read_MEA(hed_path, start, end, electrode_distance)
```

- 戻り値の `mea` が、これ以降すべての解析の**起点**
- `start`〜`end` 秒だけ読むので**メモリを節約**できる

<div class="note">

**補足**：`electrode_distance`（電極間距離）は伝導速度などの計算に使う値です。お使いの MEA チップに合わせて指定します（例では 450μm）。

</div>

---

## フィルターありで読み込む

ノイズ処理をかけたいときは、第5引数に `FilterType` を指定します。

```python
# 神経細胞 → 移動平均フィルター
mea = read_MEA(hed_path, start, end,
               electrode_distance, FilterType.FILTER_MEA)

# 心筋細胞 → 平均波形（拍動を重ね合わせて平滑化）
mea = read_MEA(hed_path, start, end,
               electrode_distance, FilterType.CARDIO_AVE_WAVE)
```

<div class="tip">

**ポイント**：指定しなければ `FilterType.NONE`（フィルターなし）。まずは**なしで読み込み、波形を見てから**フィルターを検討するのがおすすめです。

</div>

---

## データの切り出し・変換

読み込んだ後でも、自由に加工できます。

```python
# 0.25〜0.5 秒の区間だけ切り出す（小数でも指定OK）
mea_slice = mea.from_slice(0.25, 0.5)

# 時刻を 0 秒始まりにそろえる
mea = mea.init_time()

# データを 1/10 に間引いて処理を高速化
mea_light = mea.down_sampling(10)
```

<div class="note">

**重要な性質**：これらの操作は**元の `mea` を書き換えず**、加工後の**新しいデータ**を返します。元データが壊れないので、安心して何度でも試せます。

</div>

---

## データの保存・再読み込み（.npz）

MEAデータは容量が大きいので、解析の中間結果を**軽量な `.npz`** で保存して使い回せます。

```python
# 保存（既定の int16 で約 1/2 サイズに圧縮）
mea.save_npz("data.npz")

# 再読み込み（電極間距離も復元されるので引数不要・高速）
mea = read_MEA_npz("data.npz")
```

- `.hed` から読み直すより**速く・軽く**、区間を切り出した後の保存にも便利
- 振幅の絶対値を厳密に保ちたいときは `mea.save_npz("data.npz", dtype="float32")`

<div class="note">

**⚠️ 必ず守る**：`.npz` は元データから作った**軽量コピー**です。**計測生データ（`.hed` / `.bio`）は必ずバックアップとして残し、削除しないでください。**

</div>

---

## 一括変換CLI「mea2npz」

たくさんの計測ファイルを**まとめて `.npz` 変換**できる **Python不要の単一バイナリCLI** も用意しています。

```bash
# インストール（初回1回だけ。Go/Python不要）
curl -fsSL https://raw.githubusercontent.com/kkito0726/MEA_modules/main/tools/mea2npz/install.sh | bash

# フォルダ内の .hed をまとめて変換（output/ に出力）
mea2npz ./measurements -recursive

# 引数なしなら対話モード（フラグを覚えなくてOK）
mea2npz
```

- 出力は `read_MEA_npz()` でそのまま読め、pyMEA生成物と**数値一致**
- 大量データの前処理を**手早く・自動で**済ませたいときに最適

<div class="tip">

**📘 ドキュメント**：かんたんマニュアル（初心者向け）
`docs/mea2npz_manual.md` ／ ツール詳細 `tools/mea2npz/README.md`

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 3. ピーク抽出

波形の「山・谷」を自動で見つける

---

## ピーク抽出とは？

電位波形の中から、**心筋・神経が活動した瞬間（とがった部分）** を自動で拾う処理です。用途に応じて3種類あります。

| 関数 | 拾う向き | よく使う場面 |
|------|---------|------------|
| `detect_peak_neg()` | 下ピーク（谷） | 心筋でよく使う |
| `detect_peak_pos()` | 上ピーク（山） | 上向きの信号 |
| `detect_peak_all()` | 上下の両方 | まとめて確認 |

<div class="tip">

**ポイント**：迷ったらまず `detect_peak_neg()`。最もよく使う基本の関数です。

</div>

---

## ピーク抽出 — サンプルコード

```python
# 下ピークを抽出（最もよく使う）
peak_index_neg = detect_peak_neg(mea.data)

# うまく拾えないときは閾値（threshold）を調整
peak_index_neg = detect_peak_neg(mea.data, threshold=2)

# 電極 ch5 の「最初のピークが起きた時刻（秒）」を取得
time = mea.data[0][peak_index_neg[5]]
```

- `peak_index_neg` は「**何番目のデータ点か**」を表すインデックスの配列
- `mea.data[0]` が**時間データ**（先頭が時間軸）
- **電極番号は 1〜64**（`mea.data[1]`〜`mea.data[64]` が各電極）

<div class="note">

**つまずきポイント**：ピークが多すぎ／少なすぎるときは `threshold` を上下させて調整します。次章の `plotPeaks` で目で確かめながら決めるのが確実です。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 4. グラフ描画

データは「見て」理解する

---

## 64電極を一覧表示

8×8 の全電極の波形を、一枚にまとめて表示します。

```python
# 0〜1秒、電位の表示範囲は ±300 μV
mea.fig.showAll(start=0, end=1,
                volt_min=-300, volt_max=300)
```

- 全64電極の波形を**俯瞰**できる（どこが活発か一目でわかる）
- 引数なしの `mea.fig.showAll()` でも動作する

<div class="tip">

**ポイント**：`volt_min` / `volt_max` は縦軸（電位）の表示範囲。波形が見切れたり潰れたりするときに調整します。

</div>

---

## 1電極を拡大表示

気になった電極だけを、大きく詳しく見ます。

```python
# 電極 ch2 の波形を拡大表示
mea.fig.showSingle(ch=2, start=0, end=1,
                   volt_min=-300, volt_max=300)
```

<div class="note">

**補足**：`showAll` で全体を見て「これは？」と思った電極を、`showSingle` で深掘りする——この**俯瞰→拡大**の流れが解析の基本です。

</div>

---

## ピークをプロットして確認

検出したピークが**正しい位置か**を波形に重ねて確認します。

```python
peak_index = detect_peak_neg(mea.data)

# ch2 の波形にピークを重ねて表示
mea.fig.plotPeaks(2, peak_index,
                  start=0, end=1,
                  volt_min=-300, volt_max=300)
```

- 波形の上に**マーカー**でピーク位置が表示される
- ピークがズレている／拾いすぎているときは `threshold` を再調整

<div class="tip">

**ポイント**：数値計算の前に必ずこれでチェック。**ピーク検出の精度が解析結果の精度**を決めます。

</div>

---

## 拍動波形の重ね合わせ

各拍動の**1stピークを基準**に切り出して重ね描くと、ばらつきが一目でわかります。

```python
import matplotlib.pyplot as plt

ch = 3                              # 重ね合わせる電極
before_sec, after_sec = 0.05, 0.3  # ピーク前後の切り出し秒数
sr = mea.data.SAMPLING_RATE
peaks = detect_peak_neg(mea.data)

# 秒 → フレーム数（from_slice の引数はフレーム番号）
before, after = int(before_sec * sr), int(after_sec * sr)

# 各ピーク前後を切り出し、時刻を0に揃えて重ね描き
mea_list = [mea.from_slice(i - before, i + after).init_time()
            for i in peaks[ch]]
plt.figure()
for m in mea_list:
    plt.plot(m.data[0], m.data[ch])
plt.ylim(-50, 150); plt.show()
```

<div class="note">

**重要**：`from_slice` の引数は**フレーム番号**。秒は `SAMPLING_RATE` を掛けて変換します。

</div>

---

## ラスタープロット & ヒストグラム

複数電極の発火タイミングを、まとめて俯瞰します。

```python
peak_index = detect_peak_neg(mea.data)
eles = [1, 2, 3, 4, 5]   # 見たい電極番号を指定

# ラスタープロット（発火タイミングを点で並べる）
mea.fig.raster_plot(peak_index=peak_index,
                    eles=eles, start=0, end=30)

# ヒストグラム（時間ごとの発火数を棒グラフに）
mea.fig.mkHist(peak_index=peak_index,
               eles=eles, start=0, end=30)
```

<div class="note">

**使いどころ**：ラスタープロットは「いつ・どの電極が」発火したか、ヒストグラムは「全体でどれくらい」発火したかを見るのに便利です。

</div>

---

## カラーマップ描画

活動電位が**どの向きに伝わったか**を、空間的に可視化します。

```python
peak_index = detect_peak_neg(mea.data)

# 2D カラーマップ（伝播方向の矢印つき）
mea.fig.draw_2d(peak_index=peak_index)

# 3D カラーマップ（立体的に表示）
mea.fig.draw_3d(peak_index=peak_index)
```

<div class="tip">

**ポイント**：色の濃淡＝興奮の到達タイミング。**興奮がどこから始まり、どこへ広がったか**が直感的にわかります。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 5. 動画作成

時間変化を GIF で見せる

---

## GIF 動画を作る

`isBuf=True` で各コマ（フレーム）を画像として貯め、つなげて動画にします。

```python
# 0.1秒ずつ時間をずらした100フレームのGIF
fig_images = [
    mea.fig.showAll(0 + i*0.1, 1 + i*0.1,
                    isBuf=True, dpi=100)
    for i in range(100)
]

video = VideoMEA(fig_images)
video.save_gif("output.gif", duration=0.1)   # ファイル保存
video.display_gif(duration=0.1)              # Jupyter上で再生
```

<div class="note">

**仕組み**：`isBuf=True` は「画面に出さず画像として返す」スイッチ。それをリストに集めて `VideoMEA` に渡すと動画になります。

</div>

---

## カラーマップ動画

カラーマップ系は `isBuf=True` を付けるだけで、**自動で動画**になります。

```python
peak_index = detect_peak_neg(mea.data)

# 拍動の周期ごとにフレームが自動生成される
video = mea.fig.draw_2d(peak_index=peak_index,
                        isBuf=True)

video.save_gif("colormap.gif", duration=0.1)
```

<div class="tip">

**ポイント**：手動でループを書かなくてOK。**興奮伝播のアニメーション**が手軽に作れます。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 6. 数値計算

ISI / FPD / 伝導速度を求める

---

## ISI（拍動間隔）の計算

ISI = **Inter-Spike Interval**。隣り合うピークの**時間間隔**で、拍動リズムの指標になります。

```python
peak_index = detect_peak_neg(mea.data)

# ch2 の ISI を計算
isi = mea.calculator.isi(peak_index, ch=2)

isi.mean  # 平均値
isi.std   # 標準偏差
isi.se    # 標準誤差
isi.stv   # Short-Term Variability（拍動の揺らぎ）
isi.coefficient_of_variation  # 変動係数（CV）
```

<div class="tip">

**ポイント**：`.mean` や `.std` のように**ドットで欲しい統計量を取り出す**だけ。計算式を書く必要はありません。

</div>

---

## FPD（細胞外電位継続時間）

FPD = **Field Potential Duration**。心筋の活動電位の長さに相当し、**QT間隔**に対応する重要指標です。

```python
peak_index = detect_peak_neg(mea.data)

# ch2 の FPD を計算
fpd = mea.calculator.fpd(peak_index, ch=2)

fpd.mean   # 平均値
fpd.std    # 標準偏差

# 検出位置を目で確認
fpd.show()
```

<div class="note">

**補足**：`fpd.show()` で検出点を可視化できます。**数値を信じる前に、まず目で確認**する習慣をつけましょう。

</div>

---

## 伝導速度の計算

2つの電極間で、信号が**到達する時間差**から興奮の伝わる速さを求めます。

```python
peak_index = detect_peak_neg(mea.data)

# ch9 → ch54 間の伝導速度
cv = mea.calculator.conduction_velocity(
    peak_index, ch1=9, ch2=54
)

cv.mean  # 平均（m/s）
cv.std   # 標準偏差
```

<div class="tip">

**ポイント**：読み込み時に指定した `electrode_distance`（電極間距離）が、ここで速度の計算に効いてきます。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# まとめ

全体の流れをおさらい

---

## 基本の流れ（コピペで動く）

```python
from pyMEA import *

# 1. データ読み込み
mea = read_MEA("data.hed", start=0, end=30,
               electrode_distance=450)

# 2. ピーク抽出
peaks = detect_peak_neg(mea.data)

# 3. グラフで確認
mea.fig.showAll()
mea.fig.plotPeaks(2, peaks)

# 4. 数値計算
isi = mea.calculator.isi(peaks, ch=2)
print(f"ISI 平均: {isi.mean:.3f} s")
```

<div class="tip">

**この4ステップが全解析の土台**：読み込む → 拾う → 見る → 計算する。

</div>

---

## チートシート

| やりたいこと | コード |
|------------|--------|
| データ読み込み | `read_MEA(path, start, end, dist)` |
| ピーク抽出 | `detect_peak_neg(mea.data)` |
| 全波形表示 | `mea.fig.showAll()` |
| 1電極表示 | `mea.fig.showSingle(ch=N)` |
| ピーク確認 | `mea.fig.plotPeaks(N, peaks)` |
| ISI計算 | `mea.calculator.isi(peaks, ch=N)` |
| FPD計算 | `mea.calculator.fpd(peaks, ch=N)` |
| GIF保存 | `VideoMEA(frames).save_gif("out.gif")` |

---

<!-- _class: lead -->
<!-- _paginate: false -->

# お疲れ様でした！

<span class="lead-sub">まずは手元のデータで「読み込み → 表示」から試してみましょう</span>

詳細は **`README_ja.md`** を参照してください
