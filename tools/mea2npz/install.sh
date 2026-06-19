#!/usr/bin/env bash
# mea2npz ワンライナーインストーラ
#
#   curl -fsSL https://raw.githubusercontent.com/kkito0726/MEA_modules/main/tools/mea2npz/install.sh | bash
#
# OS/アーキを自動判定し、GitHub Releases から該当バイナリを取得して ~/bin に配置する。
# git bash(Windows) / macOS / Linux で動作する。Go/Python は不要。
set -euo pipefail

REPO="kkito0726/MEA_modules"
BINDIR="${HOME}/bin"

# --- OS/アーキ判定 ---
uname_s="$(uname -s)"
uname_m="$(uname -m)"

case "${uname_s}" in
  Linux*)                 os="linux";   ext="" ;;
  Darwin*)                os="darwin";  ext="" ;;
  MINGW*|MSYS*|CYGWIN*)   os="windows"; ext=".exe" ;;
  *) echo "未対応のOSです: ${uname_s}" >&2; exit 1 ;;
esac

case "${uname_m}" in
  x86_64|amd64)  arch="amd64" ;;
  arm64|aarch64) arch="arm64" ;;
  *) echo "未対応のアーキテクチャです: ${uname_m}" >&2; exit 1 ;;
esac

# Windows は amd64 のみ配布
if [ "${os}" = "windows" ]; then arch="amd64"; fi

asset="mea2npz-${os}-${arch}${ext}"
url="https://github.com/${REPO}/releases/latest/download/${asset}"

echo "OS/アーキ: ${os}/${arch}"
echo "取得元:   ${url}"

mkdir -p "${BINDIR}"
dest="${BINDIR}/mea2npz${ext}"

# --- ダウンロード ---
if command -v curl >/dev/null 2>&1; then
  curl -fSL "${url}" -o "${dest}"
elif command -v wget >/dev/null 2>&1; then
  wget -O "${dest}" "${url}"
else
  echo "curl も wget も見つかりません" >&2; exit 1
fi
chmod +x "${dest}"

echo ""
echo "インストール完了: ${dest}"
case ":${PATH}:" in
  *":${BINDIR}:"*) echo "新しいシェルで 'mea2npz' を実行できます。" ;;
  *) echo "注意: ${BINDIR} が PATH にありません。git bash では新しいシェルを開けば自動で追加されます。"
     echo "      手動で通す場合: export PATH=\"${BINDIR}:\$PATH\"" ;;
esac
