# WSL 開発環境構築ガイド（git / gh / Claude Code）

Windows の WSL2（Ubuntu）上に開発に必要なツールを導入する手順書です。

**前提**: Docker Desktop をインストール済みで、WSL2 + Ubuntu が使える状態であること。

ターミナルは **Windows ターミナル** または **WSL** を直接起動して使用してください。

---

## ステップ 1：パッケージを最新化する

まず Ubuntu のパッケージ情報を最新にしておきます。

```bash
sudo apt update && sudo apt upgrade -y
```

---

## ステップ 2：Git を導入する

```bash
sudo apt install -y git
```

インストール確認:

```bash
git --version
# git version 2.x.x と表示されれば OK
```

### Git の初期設定

コミット時に使う名前とメールアドレスを設定します。

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## ステップ 3：GitHub CLI（gh）を導入する

> **gh とは？** GitHub をコマンドラインで操作するツールです。PR の作成やリポジトリのクローンなどをターミナルから行えます。

### インストール

```bash
sudo apt install -y curl

curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

sudo apt update && sudo apt install -y gh
```

インストール確認:

```bash
gh --version
# gh version x.x.x と表示されれば OK
```

### GitHub にログイン

```bash
gh auth login
```

対話形式で以下を選択します。

```
? What account do you want to log into?
  → GitHub.com

? What is your preferred protocol for Git operations?
  → HTTPS

? Authenticate Git with your GitHub credentials?
  → Yes

? How would you like to authenticate GitHub CLI?
  → Login with a web browser
```

ブラウザが自動で開くので、表示されたコードを入力して認証を完了してください。

認証確認:

```bash
gh auth status
# Logged in to github.com as <あなたのユーザー名> と表示されれば OK
```

---

## ステップ 4：Claude Code を導入する

> **Claude Code とは？** Anthropic が提供する AI コーディングアシスタントです。ターミナルから自然言語で開発作業を指示できます。

### インストール

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

インストール確認:

```bash
claude --version
# claude x.x.x と表示されれば OK
```

### 初回認証

```bash
claude
```

初回起動時にブラウザが開き、Anthropic アカウントでのログインを求められます。ログイン後、ターミナルに戻ると使用できます。

---

## 最終確認

すべて導入できたか一括確認します。

```bash
git --version && gh --version && claude --version
```

3つすべてバージョンが表示されれば環境構築完了です。

---

## 次のステップ

Dev Container を使った MEA 解析環境の構築は `devcontainer_guide.md` を参照してください。
