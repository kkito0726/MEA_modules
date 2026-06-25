---
marp: true
theme: default
paginate: true
footer: 'mea2npz manual'
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg: #f4f6fb;
  --bg-2: #eaedf7;
  --ink: #1d2440;
  --muted: #6b7390;
  --indigo: #4f46e5;
  --violet: #7c3aed;
  --cyan: #06b6d4;
  --accent: #4f46e5;
  --card: #ffffff;
  --code-bg: #161b2e;
  --code-fg: #e6e9f5;
  --code-line: #2a3150;
  --font-default: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif;
  --font-disp: 'Space Grotesk', 'Noto Sans JP', sans-serif;
  --font-code: 'JetBrains Mono', 'Consolas', monospace;
}

section {
  background:
    radial-gradient(1100px 500px at 110% -10%, rgba(124,58,237,0.10), transparent 60%),
    radial-gradient(900px 500px at -10% 120%, rgba(6,182,212,0.10), transparent 60%),
    linear-gradient(135deg, var(--bg) 0%, var(--bg-2) 100%);
  color: var(--ink);
  font-family: var(--font-default);
  font-weight: 500;
  box-sizing: border-box;
  position: relative;
  line-height: 1.7;
  font-size: 21px;
  padding: 62px 66px;
}

section::before {
  content: '';
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 8px;
  background: linear-gradient(180deg, var(--indigo), var(--violet) 50%, var(--cyan));
}

h1, h2, h3, h4 { margin: 0; padding: 0; font-family: var(--font-disp); }

h1 {
  font-size: 66px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -1px;
  color: var(--ink);
}

h2 {
  font-size: 38px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--ink);
  margin-bottom: 30px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(29,36,64,0.12);
}

h2::before {
  content: '';
  display: inline-block;
  width: 14px; height: 14px;
  margin-right: 16px;
  border-radius: 4px;
  background: linear-gradient(135deg, var(--indigo), var(--cyan));
  transform: translateY(-2px);
}

h3 {
  color: var(--indigo);
  font-size: 24px;
  font-weight: 700;
  margin-top: 22px;
  margin-bottom: 10px;
}

ul, ol { padding-left: 26px; }
li { margin-bottom: 11px; }
li::marker { color: var(--indigo); }

pre {
  background: var(--code-bg);
  border: 1px solid var(--code-line);
  border-radius: 14px;
  padding: 18px 22px;
  overflow-x: auto;
  font-family: var(--font-code);
  font-size: 16px;
  line-height: 1.55;
  color: var(--code-fg);
  box-shadow: 0 18px 40px rgba(29,36,64,0.18);
}

pre code { background: transparent; padding: 0; color: var(--code-fg); font-weight: 400; }

code {
  background: rgba(79,70,229,0.10);
  color: var(--indigo);
  padding: 2px 8px;
  border-radius: 6px;
  font-family: var(--font-code);
  font-size: 0.85em;
  font-weight: 600;
}

table {
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
  font-size: 19px;
  margin-top: 6px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 14px 34px rgba(29,36,64,0.10);
}

th {
  background: linear-gradient(135deg, var(--indigo), var(--violet));
  color: #fff;
  font-weight: 700;
  text-align: left;
  padding: 12px 18px;
  font-family: var(--font-disp);
}

td {
  padding: 11px 18px;
  border-bottom: 1px solid #e7eaf3;
  background: var(--card);
}

tr:nth-child(even) td { background: #f7f8fc; }
tr:last-child td { border-bottom: none; }

blockquote {
  background: rgba(79,70,229,0.06);
  border-left: 4px solid var(--indigo);
  border-radius: 10px;
  padding: 12px 20px;
  margin-top: 22px;
  color: #3b4163;
  font-size: 18px;
}

footer {
  font-size: 13px;
  color: var(--muted);
  font-family: var(--font-code);
  position: absolute;
  left: 66px;
  bottom: 28px;
  letter-spacing: 1px;
}

section::after { color: var(--muted); font-family: var(--font-code); }

section.lead {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background:
    radial-gradient(800px 600px at 100% 0%, rgba(124,58,237,0.18), transparent 55%),
    radial-gradient(800px 600px at 0% 100%, rgba(6,182,212,0.16), transparent 55%),
    linear-gradient(135deg, #1a1f3a 0%, #232a52 100%);
  color: #eef1fb;
}

section.lead::before {
  background: linear-gradient(180deg, var(--cyan), var(--violet));
}

section.lead footer { display: none; }

section.lead h1 {
  color: #ffffff;
  margin-bottom: 22px;
}

section.lead .grad {
  background: linear-gradient(120deg, #a5b4fc, #67e8f9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

section.lead p {
  font-size: 23px;
  color: #d7ddf2;
  font-weight: 500;
}

section.lead .sub {
  color: #8b93bf;
  font-size: 18px;
  font-family: var(--font-code);
}

section.lead strong { color: #7ee7ff; }

strong { color: var(--indigo); font-weight: 700; }

.flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-top: 38px;
  flex-wrap: wrap;
}

.flow .box {
  background: var(--card);
  border: 1px solid #dfe3f2;
  border-radius: 14px;
  padding: 20px 26px;
  text-align: center;
  font-weight: 700;
  font-family: var(--font-disp);
  font-size: 19px;
  min-width: 168px;
  box-shadow: 0 12px 28px rgba(29,36,64,0.10);
}

.flow .box.hi {
  background: linear-gradient(135deg, var(--indigo), var(--violet));
  color: #fff;
  border: none;
}

.flow .box small {
  display: block;
  color: var(--muted);
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-default);
  margin-top: 6px;
}

.flow .box.hi small { color: #d7d9f5; }

.flow .arrow { color: var(--violet); font-size: 26px; font-weight: 700; }
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

# mea2npz

<p>MEA計測データを <strong>軽い .npz</strong> へ。<br>速く、シンプルに。</p>
<p class="sub">.hed / .bio  →  .npz  converter</p>

---

## 流れ

- **What** — このツールでできること
- **Setup** — インストール（1回だけ）
- **Run** — 対話モードとコマンド
- **More** — 一括変換・中身の確認
- **Help** — エラー別の対処

---

## できること

`.hed` / `.bio` は **サイズが大きく** 持ち運びが大変。
`mea2npz` がこれを **軽い `.npz`** に変換します。

<div class="flow">
  <div class="box">.hed / .bio<small>大きい生データ</small></div>
  <div class="arrow">→</div>
  <div class="box hi">.npz<small>軽い・1/4〜1/2</small></div>
  <div class="arrow">→</div>
  <div class="box">pyMEA<small>解析・グラフ化</small></div>
</div>

---

## 3つの強み

- **Python 不要**
  実行ファイル1つを置くだけで動く
- **マルチOS対応**
  Windows / Mac / Linux で同じ操作
- **完全に同じ数値**
  変換した `.npz` は pyMEA でそのまま読める

---

## 用語ガイド

| 言葉 | かんたんな意味 |
|---|---|
| **MEA** | 多数の電極で細胞の電気信号を測る装置 |
| **`.hed`** | 計測の設定が入った小さなファイル |
| **`.bio`** | 実際の電位データ（大きなかたまり） |
| **`.npz`** | 変換後の軽いファイル |
| **ターミナル** | コマンドを打つ画面（Winは git bash） |

> `.hed` と `.bio` はセットで1計測。`.hed` を渡せば `.bio` は自動で探します。

---

## インストール

最初の **1回だけ**。ターミナルに貼り付けて Enter。

```bash
curl -fsSL https://raw.githubusercontent.com/kkito0726/MEA_modules/main/tools/mea2npz/install.sh | bash
```

- **Windows** — スタートメニューで `git bash` を開いて実行
- **Mac / Linux** — ターミナルを開いて実行
- 完了後、ターミナルを **開き直す**

```bash
mea2npz -version   # 文字が出れば成功
```

> Mac で開けない時 → `xattr -d com.apple.quarantine ~/bin/mea2npz`

---

## いちばん簡単

**対話モード** — 質問に答えるだけで変換できます。

```bash
mea2npz
```

```
入力パス (.hed ファイル or ディレクトリ): sample.hed
保存dtype (int16/float32) [int16]:        ← Enter でOK
読み込み時間を指定する [Y/n]: n            ← 全部なら n
電極間距離 (μm) [450]:                     ← 450 なら空欄のまま Enter
変換完了: sample.npz
```

> **電極間距離はたいてい 450** → 何も入れず **Enter**（空欄）でOK。
> ファイルは **ドラッグ＆ドロップ** で入力できます。

---

## 質問の意味

| 質問 | 意味 | 迷ったら |
|---|---|---|
| 入力パス | 変換したい `.hed` の場所 | 必須 |
| 保存dtype | 圧縮方式（int16=軽い） | `int16` |
| 時間を指定 | 一部だけ切り出すか | `n`（全部） |
| 電極間距離 | 電極の間隔(μm) | **`450` なら空欄でOK** |
| 時刻リセット | 切出しを0秒開始にする | Enter |
| 出力先 | 保存先 | Enter（同じ場所） |

---

## コマンドで使う

慣れたら、質問なしで一発変換。

```bash
# いちばん基本（全部を int16 で変換）
mea2npz sample.hed

# 30秒〜60秒だけ切り出す
mea2npz sample.hed -start 30 -end 60

# float32 で保存する
mea2npz sample.hed -dtype float32
```

> ヘルプは `mea2npz -h` で表示されます。

---

## 主なオプション

| オプション | 意味 | 初期値 |
|---|---|---|
| `-start <秒>` | 何秒から読むか | 0 |
| `-end <秒>` | 何秒まで読むか | 最後まで |
| `-dtype` | 圧縮方式 int16/float32 | int16 |
| `-distance <μm>` | 電極間距離 | 450 |
| `-o <場所>` | 出力先を指定 | 同じ場所 |
| `-keep-time` | 時刻をリセットしない | リセット |

---

## まとめて変換

フォルダを渡すと **中身を全部** 変換します。

```bash
mea2npz ./measurements          # サブフォルダも → -recursive
```

- 結果はフォルダ内の **`output/`** にまとめて保存
- 変換できないファイルは **止まらず飛ばす**
- 最後に **成功 / スキップ / 失敗** の件数を表示

<div class="flow">
  <div class="box">フォルダ指定</div>
  <div class="arrow">→</div>
  <div class="box hi">1つずつ変換<small>失敗はSKIP</small></div>
  <div class="arrow">→</div>
  <div class="box">件数を表示</div>
</div>

---

## 中身の確認

「この `.npz` どんな設定だっけ？」は `.npz` を渡すだけ。

```bash
mea2npz sample.npz
```

| 項目 | 値 |
|---|---|
| 電極間距離 (μm) | 450 |
| サンプリングレート (Hz) | 5000 |
| GAIN | 50000 |
| 計測時間 (s) | 1 |
| dtype | int16 |

> このとき **変換はされません**。中身を見るだけなので安全です。

---

## Python で読む

pyMEA では `.hed` とほぼ同じように読めます。

```python
from pyMEA import read_MEA_npz

mea = read_MEA_npz("sample.npz")
print(mea.data.array.shape)
# (65, データ数) … 1行目は時刻、2行目以降が各電極
```

- `mea2npz` の `.npz` は pyMEA 製と **数値が完全に一致**
- これまでの **解析コードがそのまま使える**

---

## 処理の流れ

変換ボタンを押すと、中ではこう動いています。

```
あなた  ─▶  mea2npz : sample.hed を変換して！
mea2npz ─▶  ファイル : sample.hed を読む（設定）
mea2npz ─▶  ファイル : sample0001.bio を読む（電位）
mea2npz ─▶  自分     : データを軽い形に圧縮
mea2npz ─▶  ファイル : sample.npz として保存
mea2npz ◀─  あなた   : 変換完了！
```

> 中身確認のときは、**重い電位データは読まず** 設定部分だけを読みます。

---

## 困ったとき

| 症状 | 対処 |
|---|---|
| `command not found` | ターミナルを **開き直す** |
| `.bio が見つかりません` | `.hed` と `○○0001.bio` を同じ場所に |
| `end=○○s が…超えています` | `-end` を短く / 時間指定をやめる |
| `dtype は int16 または…` | `int16` か `float32` にする |
| Mac で開けない | `xattr -d com.apple.quarantine ~/bin/mea2npz` |

> エラーは赤い画面ではなく **ふつうの文字**。落ち着いて読めば原因が書いてあります。

---

<!-- _class: lead -->
<!-- _paginate: false -->

# <span class="grad">Happy Analyzing.</span>

<p>質問に答えるだけ、コマンド1つで変換完了。</p>
<p class="sub">github.com/kkito0726/MEA_modules</p>
