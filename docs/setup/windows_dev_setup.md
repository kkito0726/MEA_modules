# 快適なWindows開発環境構築

Windowsで快適に開発するための環境を一から構築する手順書です。  
プログラム本体はWSL（Windows上で動くLinux環境）に入れ、UIツールのみWindowsにインストールする構成にします。

> [!WARNING]
> **この資料はある程度コマンド操作に慣れた方向けです。**  
> プログラミング初心者の方は、まず **[devcontainer_guide.md](devcontainer_guide.md)** の手順で環境構築することを強くお勧めします。

```
Windows側         WSL（Linux）側
─────────────     ───────────────
VS Code      ←→  git
Docker Desktop←→  gh（GitHub CLI）
                  Claude Code
                  各種開発ツール
```

---

## ステップ 1：VS Code をインストールする

1. [VS Code 公式サイト](https://code.visualstudio.com/) からインストーラーをダウンロード
2. インストーラーを起動し、以下の項目にチェックを入れてインストール
   - 「PATHへの追加」
   - 「エクスプローラーのファイルコンテキストメニューに追加」（任意）

---

## ステップ 2：VS Code 拡張機能をインストールする

VS Code を起動し、左側の拡張機能アイコンから以下をインストールします。

### 必須

| 拡張機能 | ID | 用途 |
|---|---|---|
| **Remote Development** | `ms-vscode-remote.vscode-remote-extensionpack` | WSL・Dev Containerへの接続をまとめて有効にするパック |

> Remote Development をインストールすると WSL拡張機能・Dev Containers拡張機能が一括で入ります。

### 推奨

| 拡張機能 | ID | 用途 |
|---|---|---|
| **GitLens** | `eamodio.gitlens` | コード行ごとのGit履歴・変更者を表示 |
| **Japanese Language Pack** | `ms-ceintl.vscode-language-pack-ja` | VS Code のUIを日本語化 |

---

## ステップ 3：Docker Desktop をインストールする

1. [Docker Desktop 公式サイト](https://www.docker.com/products/docker-desktop/) からインストーラーをダウンロード
2. インストーラーを起動してインストール
   - 「Use WSL 2 instead of Hyper-V」にチェックが入っていることを確認
3. インストール完了後、パソコンを再起動
4. Docker Desktop を起動する（タスクバーにクジラのアイコンが表示されれば起動中）

> Docker Desktop のインストールにより、WSL2 も自動でセットアップされます。

インストール確認（後述のWSL内で実行）:

```bash
docker --version
# Docker version 2x.x.x と表示されれば OK
```

---

## ステップ 4：WSL（Ubuntu）を起動する

スタートメニューで「Ubuntu」を検索して起動します。  
初回起動時はユーザー名とパスワードの設定を求められます。

> 以降のコマンドはすべてこのUbuntuターミナル上で実行します。

パッケージを最新化しておきます。

```bash
sudo apt update && sudo apt upgrade -y
```

---

## ステップ 5：Git を導入する

```bash
sudo apt install -y git
```

インストール確認:

```bash
git --version
# git version 2.x.x と表示されれば OK
```

初期設定:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## ステップ 6：GitHub CLI（gh）を導入する

> **gh とは？** ターミナルからGitHubのPR作成・リポジトリ操作ができるツールです。

```bash
sudo apt install -y curl

curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

sudo apt update && sudo apt install -y gh
```

GitHubにログイン:

```bash
gh auth login
```

対話形式で以下を選択します。

```
? What account do you want to log into?   → GitHub.com
? What is your preferred protocol?        → HTTPS
? Authenticate Git with your GitHub credentials? → Yes
? How would you like to authenticate?     → Login with a web browser
```

ブラウザが開くのでコードを入力して認証を完了してください。

認証確認:

```bash
gh auth status
# Logged in to github.com as <ユーザー名> と表示されれば OK
```

---

## ステップ 7：Claude Code を導入する

> **Claude Code とは？** Anthropic が提供するAIコーディングアシスタントです。ターミナルから自然言語で開発作業を指示できます。

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

インストール確認:

```bash
claude --version
```

初回認証:

```bash
claude
```

ブラウザが開くのでAnthropicアカウントでログインしてください。

---

## 最終確認

```bash
git --version && gh --version && claude --version && docker --version
```

4つすべてバージョンが表示されれば環境構築完了です。

---

## VS Code から WSL に接続する

1. VS Code を起動
2. 左下の緑色の `><` アイコンをクリック
3. 「WSLへの接続」を選択

接続後、VS Code のターミナルが自動的にWSL内で開きます。以降の開発作業はこの状態で行います。

---

## 次のステップ

Dev Container を使ったMEA解析環境の構築は `devcontainer_guide.md` を参照してください。  
リポジトリのクローンは WSL 内の `~/Workspace` に行います。
