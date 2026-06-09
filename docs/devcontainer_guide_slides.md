---
marp: true
theme: default
paginate: true
html: true
backgroundColor: #fafafa
style: |
  /* ── Base ──────────────────────────────── */
  section {
    font-family: 'Hiragino Kaku Gothic Pro', 'Noto Sans JP', sans-serif;
    font-size: 26px;
    color: #1a1a2e;
    padding: 44px 64px;
    overflow-wrap: break-word;
    word-break: auto-phrase;
    line-break: strict;
  }
  h2 {
    font-size: 34px;
    color: #1565c0;
    border-bottom: 3px solid #1565c0;
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 18px;
  }
  h3 {
    font-size: 23px;
    color: #0277bd;
    margin: 14px 0 6px;
  }
  li { margin-bottom: 6px; line-height: 1.5; }
  section::after { font-size: 16px; color: #90a4ae; }

  /* ── Title slide (section.title) ─────── */
  section.title {
    color: white;
    text-align: center;
    padding-top: 130px;
  }
  section.title h1 {
    font-size: 50px;
    color: white;
    line-height: 1.35;
    margin-bottom: 20px;
  }
  section.title p { font-size: 22px; color: rgba(255,255,255,0.88); }
  section.title::after { color: rgba(255,255,255,0.5); }

  /* ── Section divider (section.divider) ─ */
  /* Background is set per-slide via _backgroundColor directive */
  section.divider {
    color: white;
    text-align: center;
    padding-top: 160px;
  }
  section.divider h2 {
    display: inline-block;
    color: white;
    border-bottom: 2px solid rgba(255,255,255,0.4);
    font-size: 42px;
    padding-bottom: 14px;
    margin-bottom: 18px;
  }
  section.divider h3 { color: rgba(255,255,255,0.8); }
  section.divider p  { color: rgba(255,255,255,0.85); font-size: 22px; }
  section.divider::after { color: rgba(255,255,255,0.45); }

  /* ── Inline code ────────────────────── */
  code {
    background: #e3f2fd;
    color: #b71c1c;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.88em;
    font-weight: 500;
  }

  /* ── Code blocks ────────────────────── */
  pre {
    background: #1e2530;
    border-radius: 10px;
    padding: 16px 22px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.25);
    margin: 10px 0;
  }
  pre code {
    background: transparent;
    color: #abb2bf;
    padding: 0;
    font-size: 0.82em;
    line-height: 1.7;
  }
  /* highlight.js トークン色をダーク背景向けに上書き */
  pre .hljs-keyword,
  pre .hljs-selector-tag { color: #c678dd; }
  pre .hljs-string,
  pre .hljs-addition      { color: #98c379; }
  pre .hljs-comment,
  pre .hljs-quote         { color: #5c6370; font-style: italic; }
  pre .hljs-number,
  pre .hljs-literal       { color: #d19a66; }
  pre .hljs-built_in,
  pre .hljs-name          { color: #61afef; }
  pre .hljs-variable,
  pre .hljs-deletion      { color: #e06c75; }
  pre .hljs-title,
  pre .hljs-function      { color: #61afef; }
  pre .hljs-attr,
  pre .hljs-meta          { color: #e5c07b; }

  /* ── Blockquote = tip / note ────────── */
  blockquote {
    background: #e3f2fd;
    border-left: 5px solid #1565c0;
    border-radius: 0 8px 8px 0;
    padding: 10px 16px;
    color: #0d47a1;
    margin: 10px 0;
    font-size: 0.9em;
  }

  /* ── Two-column cards ───────────────── */
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 8px; }
  .card {
    background: white;
    border-radius: 10px;
    padding: 16px 20px;
    border: 1px solid #bbdefb;
    box-shadow: 0 1px 5px rgba(21,101,192,0.07);
  }
  .card h3 { margin-top: 0; }

  /* ── Tables ─────────────────────────── */
  table { width: 100%; border-collapse: collapse; font-size: 22px; margin: 12px 0; }
  th { background: #1565c0; color: white; padding: 10px 14px; text-align: left; }
  td { padding: 9px 14px; border-bottom: 1px solid #e0e0e0; }
  tr:nth-child(even) td { background: #f5f9ff; }

  /* ── Compact Q&A slides ─────────────── */
  section.qa { font-size: 22px; }
  section.qa h2 { font-size: 30px; margin-bottom: 14px; }
  section.qa h3 { font-size: 21px; margin: 14px 0 3px; }
  section.qa p  { margin: 0 0 6px; }
---

<!-- _backgroundColor: #1565c0 -->
<!-- _class: title -->

# Dev Container を使った<br>開発環境構築ガイド

pyMEA の開発環境を誰でも同じようにセットアップできます

---

## このガイドについて

<div class="cols">
<div class="card">

### 対象者

- プログラミングを始めたばかりの方
- Python の環境構築でつまずいた方
- 「自分のパソコンでは動かない」経験がある方

</div>
<div class="card">

### ゴール

このガイドを終えると...

- Dev Container が起動している
- `python --version` で **Python 3.12** が表示される
- `pyMEA` がすぐに使える状態になっている

</div>
</div>

---

## Dev Container（開発コンテナ）とは？

**プログラムを動かすための「専用の箱」** をパソコンの中に作る仕組みです。

```
あなたのパソコン
┌───────────────────────────────────────────┐
│  ┌─────────────────────────────────────┐  │
│  │  Dev Container（専用の箱）          │  │
│  │  Python 3.12 + 必要なライブラリ     │  │
│  │  VS Code 拡張機能                   │  │
│  │                                     │  │
│  │  /data  ←───  外付けHDD（計測データ） │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

この「箱」の中に pyMEA を動かすために必要なものがすべて入っています。

---

## なぜ Dev Container を使うの？

<div class="cols">
<div class="card">

### 1. 「動かない」が起きない
バージョン違いによるトラブルがなくなります。
Dev Container なら **全員が全く同じ環境** で作業できます。

### 2. パソコンを汚さない
ライブラリは「箱」の中にインストール。
不要になったら **箱ごと削除** するだけ。

</div>
<div class="card">

### 3. セットアップが一瞬
「何をインストールするか」の設定がすでに用意されています。
**コマンド1つで環境が整います。**

### 4. 全員が同じ環境を使える
設定ファイルがリポジトリに含まれているため、
チームで環境を共有できます。

</div>
</div>

---

<!-- _backgroundColor: #0277bd -->
<!-- _class: divider -->

## 事前準備

4つのソフトウェアをインストールする（すべて無料）

---

## 事前準備：必要なソフトウェア 4つ

| # | ソフトウェア | 役割 |
|---|------------|------|
| **1** | **Git** | リポジトリのダウンロード・変更履歴管理 |
| **2** | **Docker Desktop** | 「専用の箱」を作るためのソフト |
| **3** | **Visual Studio Code** | コードを書くためのエディタ |
| **4** | **Dev Containers 拡張機能** | VS Code と Docker を連携させる |

---

## ステップ 1：Git をインストールする

> **Git とは？** ファイルの変更履歴を管理するツールです。プロジェクトのダウンロードにも使います。

**Windows**: `https://gitforwindows.org/` からダウンロード
→ インストーラーを起動して「Next」を押し続けるだけで OK

**Mac**: ターミナルで `git --version` を実行
→ インストールを促すダイアログが表示されたら指示に従う

```bash
git --version
# git version 2.x.x と表示されれば OK
```

---

## ステップ 2：Docker Desktop をインストールする

> **Docker とは？** 「専用の箱（コンテナ）」を作るためのソフトウェアです。

1. `https://www.docker.com/products/docker-desktop/` にアクセス
2. OS（Windows / Mac）向けのインストーラーをダウンロード
3. インストーラーを起動してインストール
4. Docker Desktop を起動（タスクバーにクジラのアイコンが表示されれば起動中）

> **Windows の注意**: WSL 2 のインストールを求められたら画面の指示に従ってください。

```bash
docker --version
# Docker version 2x.x.x と表示されれば OK
```

---

## ステップ 3 & 4：VS Code と拡張機能をインストールする

<div class="cols">
<div class="card">

### VS Code のインストール

1. `https://code.visualstudio.com/` からダウンロード
2. インストーラーを起動してインストール

</div>
<div class="card">

### Dev Containers 拡張機能

1. VS Code を起動
2. 左の **拡張機能アイコン** をクリック
3. 検索ボックスに `Dev Containers` と入力
4. **Dev Containers**（Microsoft 製）をインストール

</div>
</div>

> 事前準備はこれで完了です！

---

<!-- _backgroundColor: #1565c0 -->
<!-- _class: divider -->

## セットアップ

リポジトリのクローンから Dev Container 起動まで

---

## セットアップの全体の流れ

```
  Step 1   リポジトリをクローンする
               ↓
  Step 2   計測データの場所を登録する（初回のみ）
               ↓
  Step 3   VS Code でフォルダを開く
               ↓
  Step 4   Dev Container で再度開く
               ↓
  Step 5   環境の自動セットアップを待つ（初回のみ数分）
               ↓
           完了！
```

---

## Step 1：リポジトリをクローンする

> **クローンとは？** GitHub 上のプロジェクトを自分のパソコンにコピーすることです。

**Mac** はターミナル、**Windows** は **Git Bash** を開いて実行します。

> **Windows の注意**: コマンドプロンプトや PowerShell ではなく **Git Bash** を使ってください。
> スタートメニューで「Git Bash」と検索して起動してください。

```bash
mkdir -p ~/Workspace          # Workspace フォルダを作成
cd ~/Workspace                # 移動
git clone https://github.com/kkito0726/MEA_modules.git
```

実行後、`~/Workspace/MEA_modules` フォルダが作成されます。

---

## Step 2：計測データの場所を登録する（Windows）

> **重要**: Dev Container を開く **前** に必ず完了してください。

リポジトリフォルダ内の **`setup.bat`** をダブルクリックして実行します。

```
MEA_modules/
├── setup.bat   ← これをダブルクリック
├── pyMEA/
└── ...
```

```
データフォルダのパス: E:\MEA_data  ← 入力して Enter

設定完了！コンテナ内からは /data でアクセスできます。
```

「設定完了！」と表示されたら **VS Code を再起動** してください。

---

## Step 2：計測データの場所を登録する（Mac）

ターミナルを開いて以下のコマンドを実行します。

```bash
# パスを ~/.zshrc に追記
echo 'export MEA_DATA_PATH="/Volumes/MyHDD/MEA_data"' >> ~/.zshrc

# 設定を反映
source ~/.zshrc
```

> `/Volumes/MyHDD/MEA_data` の部分はご自身のパスに変更してください。
> Finder でフォルダを開いてアドレスバーからコピーできます。

設定後は **VS Code を再起動** してください。

コンテナ起動後は外付けHDDのデータを **`/data`** からアクセスできます：

```python
mea = read_MEA("/data/sample.hed", start=0, end=5, electrode_distance=450)
```

---

## Step 3 & 4：VS Code でフォルダを開く

```bash
code ~/Workspace/MEA_modules
```

または VS Code のメニューから「ファイル」→「フォルダーを開く」で `MEA_modules` を選択。

フォルダを開くと **右下に通知** が表示されます：

```
┌──────────────────────────────────────────────────────┐
│  フォルダーにデブコンテナー構成ファイルが含まれています。  │
│                                                        │
│     [コンテナーで再度開く]             [後で]           │
└──────────────────────────────────────────────────────┘
```

**「コンテナーで再度開く」** をクリックしてください。

> 通知が表示されない場合：VS Code 左下の **緑色の `><` アイコン** をクリック

---

## Step 5：環境の自動セットアップを待つ

初回はライブラリのダウンロード・インストールが **自動で** 行われます。

```
[初回のみ] 数分かかる場合があります
  ↓
Python 3.12 の環境を準備中...
  ↓
NumPy, SciPy, Matplotlib ... をインストール中
  ↓
VS Code 拡張機能をインストール中...
  ↓
完了！
```

VS Code の左下が以下のように変われば成功です：

```
Dev Container: Python 3
```

---

## 動作確認

Dev Container が起動したら、VS Code の **ターミナル** を開きます。
（メニュー：「ターミナル」→「新しいターミナル」）

```bash
python --version
# Python 3.12.x と表示されれば OK
```

```bash
python -c "import pyMEA; print('pyMEA が使えます！')"
# pyMEA が使えます！ と表示されれば OK
```

---

<!-- _backgroundColor: #37474f -->
<!-- _class: divider -->

## トラブルシューティング

よくある質問と解決方法

---

<!-- _class: qa -->

## よくあるトラブル（1 / 3）

### Q1. 「コンテナーで再度開く」の通知が表示されない
VS Code 左下の緑色の `><` アイコンをクリックして「コンテナーで再度開く」を選択してください。

### Q2. Docker Desktop が起動していないと言われる
Docker Desktop を起動して、クジラのアイコンが表示されるまで待ってから再度試してください。

### Q3. 「WSL 2 インストールが必要」と表示される（Windows）
表示されたリンクから WSL 2 をインストールしてください。インストール後にパソコンの再起動が必要な場合があります。

---

<!-- _class: qa -->

## よくあるトラブル（2 / 3）

### Q4. コンテナのビルドが途中で止まる
インターネット接続を確認してください。ライブラリのダウンロード中はネット接続が必要です。

### Q5. コンテナ起動時にエラーが出てデータが見つからない（Windows）
`setup.bat` を実行する前に Dev Container を開こうとした可能性があります。一度 Dev Container を閉じ、`setup.bat` を実行し、VS Code を再起動してから再度開いてください。

### Q6. `/data` の中身が空に見える
外付けHDDがパソコンに接続されているか確認してください。接続されている場合は `setup.bat`（Windows）または `~/.zshrc`（Mac）に設定したパスが正しいか確認してください。

---

## よくあるトラブル（3 / 3）：クラウドストレージ

**Q. OneDrive や Google Drive に計測データを保存している場合は？**

| ストレージ | 動作 | 対処 |
|-----------|:----:|------|
| OneDrive / Dropbox（同期済み） | OK | 「常にこのデバイスに保存する」に設定 |
| Google Drive（ミラーモード） | 不安定 | 動く場合もあるが不安定 |
| Google Drive（ストリームモード） | 不可 | Docker からアクセス不可 |

> **推奨**: MEA 計測データは1ファイルで数百MB〜数GBになることがあります。
> **外付けHDDへの保存を推奨します。** クラウドストレージはバックアップ用途にとどめてください。

---

## アップデート方法

開発者から「アップデートしてください」と連絡が来たとき：

<div class="cols">
<div class="card">

### Step 1：最新コードを取得する

VS Code のターミナルを開いて実行：

```bash
git pull
# Updating abc1234..def5678
```

</div>
<div class="card">

### Step 2：コンテナを再ビルドする

VS Code 左下の `Dev Container: Python 3` をクリック
→ **「コンテナーのリビルド」** を選択

または `F1` → `rebuild` と検索して選択

</div>
</div>

---

<!-- _backgroundColor: #2e7d32 -->
<!-- _class: divider -->

## 環境構築が完了しました！

次のステップ：`README_ja.md` を参照して pyMEA の使い方を確認してください。

Jupyter Notebook でのデータ解析も、同じ Dev Container 環境でそのまま使えます。
`.ipynb` ファイルを開くだけで使えます。
