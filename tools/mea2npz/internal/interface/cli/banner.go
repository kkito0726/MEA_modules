package cli

import (
	"fmt"
	"io"
	"os"
)

// bannerArt は起動時に表示する mea2npz の ASCII アート(figlet ANSI Shadow 相当)。
// Go の raw 文字列に収めるためバッククォート/バックスラッシュを含まないフォントを選んでいる。
const bannerArt = `
███╗   ███╗███████╗ █████╗ ██████╗ ███╗   ██╗██████╗ ███████╗
████╗ ████║██╔════╝██╔══██╗╚════██╗████╗  ██║██╔══██╗╚══███╔╝
██╔████╔██║█████╗  ███████║ █████╔╝██╔██╗ ██║██████╔╝  ███╔╝
██║╚██╔╝██║██╔══╝  ██╔══██║██╔═══╝ ██║╚██╗██║██╔═══╝  ███╔╝
██║ ╚═╝ ██║███████╗██║  ██║███████╗██║ ╚████║██║     ███████╗
╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝     ╚══════╝
`

const (
	author        = "kkito0726"
	license       = "MIT"
	repoURL       = "https://github.com/kkito0726/MEA_modules"
	copyrightYear = "2026"
)

// printBanner は起動バナー(アート + バージョン + リポジトリURL)を表示する。
// color=true のとき端末向けに色付けする。
func printBanner(w io.Writer, color bool) {
	if color {
		fmt.Fprintf(w, "\033[36m%s\033[0m", bannerArt) // cyan
	} else {
		fmt.Fprint(w, bannerArt)
	}
	fmt.Fprintf(w, " :: .hed/.bio → .npz converter ::   v%s\n", Version)
	fmt.Fprintf(w, " %s\n\n", repoURL)
}

// printVersion は GNU 風の --version 出力(バージョン + 著作権 + ライセンス + 著者)を表示する。
func printVersion(w io.Writer) {
	fmt.Fprintf(w, "mea2npz %s\n", Version)
	fmt.Fprintf(w, "Copyright (C) %s %s\n", copyrightYear, author)
	fmt.Fprintf(w, "License: %s\n", license)
	fmt.Fprintf(w, "Written by %s.\n", author)
}

// isTerminal は f が端末(文字デバイス)かどうかを返す。リダイレクト時は色付けを避けるために使う。
func isTerminal(f *os.File) bool {
	fi, err := f.Stat()
	if err != nil {
		return false
	}
	return fi.Mode()&os.ModeCharDevice != 0
}
