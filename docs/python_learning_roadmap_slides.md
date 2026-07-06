---
marp: true
theme: default
paginate: true
size: 16:9
footer: pyMEA Python 学習ロードマップ
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

/* mermaid 図（エクスポート HTML でレンダリング） */
.mermaid {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 18px;
  margin-top: 10px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(15,30,60,0.08);
}
.mermaid svg { max-height: 360px; height: auto; }
</style>

<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true, theme: 'neutral', securityLevel: 'loose' });
</script>

<!-- _class: lead -->
<!-- _paginate: false -->

# Python 学習ロードマップ

pyMEA で研究解析を自走できるようになるまで

<span class="lead-sub">プログラミング初心者向け — 何から始めればいいかがわかる道しるべ</span>

---

## このスライドのゴール

「MEA の解析を pyMEA でやりたい。でもプログラミングは初めてで、**何から手をつければいいかわからない**」——その状態を抜け出すためのスライドです。

- Python の文法を**すべて覚える必要はありません**
- pyMEA で解析するために**本当に必要な範囲だけ**を、順番に学びます
- ゴールは「用意された関数を、正しく呼び出せる」ようになること

<div class="note">

**大事な考え方**：pyMEA を使うのに、プログラムを一から作る力は要りません。必要なのは「**すでにある道具を使いこなす**」ための最小限の知識です。肩の力を抜いていきましょう。

</div>

---

## 全体像（学習マップ）

STEP 0〜10 を、下の 4 つのまとまりに分けて進みます。**核心は STEP 3・4**。ここを越えると一気にラクになります。

<div class="mermaid">
flowchart LR
  subgraph B["基礎編"]
    direction TB
    S0["STEP0 環境構築"] --> S1["STEP1 変数・print"] --> S2["STEP2 リスト・辞書"]
  end
  subgraph C["核心編 ★"]
    direction TB
    S3["STEP3 関数の呼び出し"] --> S4["STEP4 オブジェクトとメソッド"]
  end
  subgraph U["実用編"]
    direction TB
    S5["STEP5 for・内包表記"] --> S6["STEP6 import"] --> S7["STEP7 NumPy"] --> S8["STEP8 描画・出力"]
  end
  subgraph P["実践編"]
    direction TB
    S9["STEP9 解析を通す"] --> S10["STEP10 自走"]
  end
  B --> C --> U --> P
</div>

---

## このロードマップの歩き方

学習を続けるための 4 つの心構えです。焦らず、手を動かしながら進めましょう。

- **完璧を目指さない**：わからない部分があっても先へ進んでOK。使ううちに馴染みます
- **手を動かす**：読むだけでは身につきません。コードは必ず自分で打って実行しましょう
- **1 日 30 分でも十分**：STEP 1〜8 は各 30 分〜数時間。実データ解析まで数日〜2 週間が目安
- **困ったら STEP 9 を先に見る**：ゴールのコードを先に眺めると、途中の文法の意味がわかります

<div class="tip">

**ヒント**：このスライドは **Python 言語そのものの入門**です。pyMEA の機能一覧は `README_ja.md` と「pyMEA コードガイド」スライドにあります。行き来しながら進めるのがおすすめです。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 基礎編

まず「動く状態」と、変数・データのまとまり

---

## STEP 0. 環境をつくる

学ぶこと：**Python が動く環境**と **pyMEA** をパソコンに用意します。まずは「コードを実行できる状態」を作るのが最優先です。

| 方法 | 向いている人 |
|---|---|
| **A. Dev Container（推奨）** | 環境構築で悩みたくない人・VS Code を使う人 |
| **B. PC に直接インストール** | すでに Python が入っている人 |

方法 B では Python 3.12 を入れたあと、ターミナルで次を実行します。

```bash
pip install git+https://github.com/kkito0726/MEA_modules.git
```

<div class="note">

**到達目標**：`from pyMEA import read_MEA` を実行してエラーが出なければ成功です。研究解析では、その場でグラフを確認できる **Jupyter Notebook（.ipynb）** を使うのが便利です。

</div>

---

## STEP 1. 変数・print・実行

学ぶこと：**変数への代入**、`print()` での表示、コメント（`#`）、数値と文字列の違い。プログラムの一番の基本です。

```python
# これはコメント。# 以降は実行されません
start = 0            # 数値（整数）を変数に入れる
message = "解析開始"   # 文字列は "..." で囲む
print(message)       # → 解析開始 と表示される
```

pyMEA のコードも「**設定値を変数に入れて、関数に渡す**」の繰り返しです。実際のサンプルでも冒頭で設定をまとめます。

```python
HEDFILE_PATH = "path/to/your_file.hed"  # ファイルの場所（文字列）
ELECTRODE_DISTANCE = 450                # 電極間距離 μm（数値）
START, END = 0, 5                       # 多重代入：2つを同時に代入
```

<div class="tip">

**到達目標**：変数に値を入れ、`print()` で表示できる。`start, end = 0, 5` のような**多重代入**が読める。

</div>

---

## STEP 2. リスト・辞書

学ぶこと：複数の値をまとめる **リスト `[ ]`**、値の組 **タプル `( )`**、キーで引く **辞書** の基本と、値の取り出し方。

```python
eles = [1, 2, 3, 4, 5]   # リスト：値を順番に並べたもの
print(eles[0])           # → 1（番号は 0 から始まる点に注意！）
```

pyMEA では、描画したい**電極番号をリストで渡す**場面が頻出します。

```python
eles = [1, 2, 3, 4, 5]                       # 描画したい電極
mea.fig.raster_plot(peak_index=peak_index, eles=eles)
```

ピーク検出の結果は「**電極番号 → その電極のピーク**」の辞書のような形。`[ ]` に番号を入れて取り出します。

```python
peak_index_neg = detect_peak_neg(mea.data)
peak_index_neg[5]   # ch 5 のピークを取り出す
```

<div class="note">

**到達目標**：リストを作り `[番号]` で要素を取り出せる。「番号は 0 から始まる」を理解している。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 核心編 ★

ここが pyMEA 攻略のカギ

---

## STEP 3. 関数の呼び出し方 ①

学ぶこと：**位置引数**と**キーワード引数（名前付き引数）**。pyMEA のコードの 8 割は「関数を引数付きで呼ぶ」だけです。ここが一番大事。

```python
# 位置引数：書いた順番で渡す
mea = read_MEA(hed_path, start, end, electrode_distance)

# キーワード引数：名前を指定して渡す（順番を気にせず・意味が明快）
mea = read_MEA(hed_path, start=0, end=5, electrode_distance=450)

# ↑ どちらも戻り値を変数 mea で受け取っている
```

<div class="note">

**ポイント**：`引数名=値`（`start=0`）の形が**キーワード引数**です。数が増えても「何を渡しているか」が一目でわかるので、初心者にはこちらがおすすめです。

</div>

---

## STEP 3. 関数の呼び出し方 ②

pyMEA の関数には**デフォルト値つきの引数**が多く、**指定しなければ既定値が使われます**。だから最初は少ない引数だけで動きます。

```python
peak_index_neg = detect_peak_neg(mea.data)              # threshold は既定値 3
peak_index_pos = detect_peak_pos(mea.data, threshold=2) # 必要な分だけ上書き
```

ドキュメントの「シグネチャ（引数一覧）」はこう読みます。

```python
def read_MEA(
    hed_path: str,               # : str は「文字列を渡す」の意味
    start: int,                  # : int は「整数を渡す」
    end: int,
    electrode_distance: int,
    filter_type=FilterType.NONE, # = つきは省略可能（デフォルト引数）
) -> PyMEA:                      # -> は「戻り値の型」
```

<div class="tip">

**到達目標**：位置引数とキーワード引数の違いを説明できる。「`=` つきの引数は省略できる」とわかる。シグネチャを見て渡せる引数を判断できる。

</div>

---

## STEP 4. オブジェクトとメソッド ①

学ぶこと：`read_MEA()` が返す `mea` は、中に **4 つの担当役**を持っています。**ドット `.` でその担当役をたどり、機能を呼び出します。**

<div class="mermaid">
flowchart LR
  mea["mea（PyMEA）<br/>すべての入口"] --> data["mea.data<br/>計測データ"]
  mea --> fig["mea.fig<br/>グラフ描画"]
  mea --> calc["mea.calculator<br/>数値計算 ISI/FPD/伝導速度"]
  mea --> ele["mea.electrode<br/>電極の位置情報"]
</div>

<div class="note">

**読み方**：`mea.fig.showAll()` は「`mea` の中の `fig`（描画担当）の `showAll`（全表示）を呼ぶ」と読めば OK。この形に慣れることが、pyMEA を使いこなす一番の近道です。

</div>

---

## STEP 4. オブジェクトとメソッド ②

**属性**と**メソッド**の 2 種類があります。`.` の後ろに `()` があるかどうかで見分けます。

```python
mea.data.SAMPLING_RATE          # 属性：() なし → 中の「値」を取り出す
mea.fig.showAll(0, 1)           # メソッド：() あり → 「〜して」と命令する
mea.calculator.isi(peak_index, ch=2)   # メソッド：ISI を計算して
```

メソッドの結果に、さらにメソッドをつなげる **メソッドチェーン** もあります。

```python
# ハイパスをかけた結果に、さらに共通ノイズ除去をかける
denoised = mea.data.highpass(cutoff=1).common_median_reference()
```

<div class="tip">

**到達目標**：`.` の後ろの `()` の有無で属性とメソッドを見分けられる。pyMEA の操作がほぼ `mea.○○.△△(...)` の形だと理解している。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 実用編

くり返し・import・NumPy・描画

---

## STEP 5. for・リスト内包表記

学ぶこと：`for` によるくり返しと、Python らしい短い書き方「**リスト内包表記**」。

```python
for i in range(3):
    print(i)                       # 0, 1, 2 と順に表示

squares = [i * i for i in range(5)]  # [0,1,4,9,16] を一気に作る
```

pyMEA では、**拍動ごとの波形の切り出し**や、**動画のコマ作成**で使われます。

```python
# 各ピークの前後を切り出し、時刻を 0 始まりにそろえたリスト
mea_list = [
    mea.from_slice(index - before_frame, index + after_frame).init_time()
    for index in peak_index_neg[ch]
]
```

<div class="note">

**到達目標**：`for x in リスト:` でくり返せる。リスト内包表記を見て「リストを作っているんだな」とわかる。難しければ普通の `for` で書いてから短くすればOK。

</div>

---

## STEP 6. import の仕組み

学ぶこと：ライブラリを読み込む `import` 文の 3 つの形。どのコードも必ず import から始まります。

```python
from pyMEA import *                    # ① まとめて読み込む（全部使える）
from pyMEA import read_MEA, detect_peak_neg  # ② 必要なものだけ
import matplotlib.pyplot as plt        # ③ 別名（エイリアス）をつける
```

- `from pyMEA import *` で `read_MEA`・`detect_peak_neg`・`FilterType` などがすぐ使えます
- グラフを細かく描きたいときは `import matplotlib.pyplot as plt` を併用します

<div class="tip">

**到達目標**：`from pyMEA import *` の意味がわかる。`import ... as ...` で別名をつけられると知っている。

</div>

---

## STEP 7. NumPy 配列の基礎

学ぶこと：pyMEA のデータや計算結果は **NumPy 配列**という形です。リストに似ていますが、数値計算が速く、平均なども 1 行で出せます。

```python
mea.data[0]     # 0 番目の行 = 時刻データ
mea.data[6]     # 6 番目の行 = ch 6 の電位データ
isi.values.mean()   # 配列の平均を計算
```

<div class="note">

**pyMEA の約束**：`mea.data[0]` が**時刻**、`mea.data[1]`〜`mea.data[64]` が**電極 1〜64 の電位**です。電極番号とインデックスが一致していて直感的。ただし「番号は 0 から」なので、時刻が `[0]` を占める点だけ覚えておきましょう。

</div>

<div class="tip">

**到達目標**：`配列[番号]` で行を取り出せる。`.mean()` で平均を計算できる。

</div>

---

## STEP 8. 描画と結果の出力

学ぶこと：`matplotlib` での簡単なグラフと、`f"..."`（f 文字列）での結果の整形表示。定番グラフは pyMEA が 1 行で描けますが、自分好みにするなら matplotlib を直接使います。

```python
import matplotlib.pyplot as plt
plt.figure()
plt.plot(mea.data[0], mea.data[3])   # 横軸=時刻, 縦軸=ch3 の電位
plt.xlabel("Time (s)"); plt.ylabel("Voltage (μV)")
plt.show()
```

```python
print(f"ch{CH} 平均ISI: {isi.values.mean():.4f} s")
# → ch6 平均ISI: 0.8123 s のように表示
```

<div class="note">

**到達目標**：`plt.plot()` で折れ線グラフを描ける。`f"{変数}"` で値を文章に埋め込める（`:.4f` は小数点以下 4 桁の書式指定）。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# 実践編

解析を最後まで通す・自走する

---

## STEP 9. 最初の解析を通す ①

ここまでの知識で、実データ 1 本を「**読み込み → ピーク検出 → 計算 → 表示**」まで通せます。まずは `isi_example.py` を写経（そのまま書き写して実行）しましょう。

```python
from pyMEA import detect_peak_neg, read_MEA

HEDFILE_PATH = "path/to/your_file.hed"  # ← 自分のパスに書き換える
CH = 6

mea = read_MEA(HEDFILE_PATH, start=0, end=5, electrode_distance=450)  # 1.読み込み
peak_index_neg = detect_peak_neg(mea.data)                           # 2.ピーク検出
isi = mea.calculator.isi(peak_index_neg, ch=CH)                      # 3.ISI 計算
print(f"ch{CH} 平均ISI: {isi.values.mean():.4f} s")                  # 4.表示
```

<div class="tip">

**注目**：このコードには STEP 1〜8 の要素（変数・キーワード引数・`mea.○○.△△()`・NumPy・f 文字列）が**すべて**入っています。読み解けたら基礎は卒業です。

</div>

---

## STEP 9. 最初の解析を通す ②

計算ができたら、次は**グラフで確認**しましょう。ピークが正しく取れているかを目で見るのは、解析の信頼性のうえでとても大切です。

```python
mea.fig.showAll(0, 1)                                # 64 電極の波形を一覧表示
mea.fig.plotPeaks(CH, peak_index_neg, start=0, end=1) # ピーク検出の確認
```

<div class="note">

**次の一歩**：ここまで来たら、`README_ja.md` の各セクション（FPD・伝導速度・カラーマップ・動画作成…）を、やりたいことに応じて**つまみ食い**していけます。どれも同じ `mea.○○.△△(...)` のパターンです。

</div>

<div class="tip">

**到達目標**：自分の計測データで、読み込み・ピーク検出・ISI 計算・グラフ表示を一通り実行できる。

</div>

---

## STEP 10. 自走できるようになる

最後は「知らない機能でも、自分で調べて使える」段階へ。研究解析を不自由なく進めるための武器を揃えます。

- **シグネチャを読む**：`README_ja.md` や `docs/api/` の日本語リファレンスで、渡せる引数を自分で判断
- **エラーを読む**：エラーは「どこで何が起きたか」の手がかり。まず最後の行を読む
- **`/pyMEA-codegen` を使う**：Claude Code で「ch6 の ISI を計算してグラフ表示して」と日本語で頼めばコード生成
- **mea2npz で前処理**：計測ファイルをまとめて軽量な `.npz` に変換する CLI ツール

<div class="tip">

**到達目標**：新しい機能を、ドキュメントを読んで自力で試せる。エラーが出ても落ち着いて原因を探せる。

</div>

---

## よくあるつまずきどころ

初心者が必ず一度は出会うエラーです。慌てず、原因を 1 つずつ確認しましょう。

| 症状 | よくある原因 | 対処 |
|---|---|---|
| `ModuleNotFoundError` | pyMEA 未インストール／別環境で実行 | STEP 0 を再確認。実行中の環境をチェック |
| `FileNotFoundError` | `.hed` のパス間違い | 綴り・場所を確認。Windows は `\`→`/` |
| `SyntaxError` | 全角スペース・閉じ忘れ | エラー行の前後、全角文字混入を確認 |
| `IndentationError` | 行頭の空白ズレ | `for`/`def` の中は半角スペース4つ |
| グラフが出ない | `plt.show()` 忘れ | Jupyter で実行 or `plt.show()` を追加 |

---

## 学習リソース・関連ドキュメント

Python そのものの入門は、必要になった文法をその都度調べるスタイルが挫折しにくくおすすめです。

| 範囲 | 参考リソース |
|---|---|
| Python 全般 | Python 公式チュートリアル（日本語） |
| NumPy | NumPy: the absolute basics for beginners |
| matplotlib | Matplotlib チュートリアル |

<div class="note">

**リポジトリ内の関連資料**：詳しい本文版は `docs/python_learning_roadmap.md`。機能一覧は `README_ja.md`／「pyMEA コードガイド」スライド。環境構築は `docs/setup/devcontainer_guide.md`。API 詳細は `docs/api/`。

</div>

---

<!-- _class: lead -->
<!-- _paginate: false -->

# まとめ

**核心は STEP 3・4**。関数の呼び出し方と `mea.○○.△△()` の読み方さえ押さえれば、あとは同じパターンの応用です。手を動かして、少しずつ前へ。
