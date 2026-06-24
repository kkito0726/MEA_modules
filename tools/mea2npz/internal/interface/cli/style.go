package cli

import "os"

// ANSI エスケープシーケンス。端末以外・NO_COLOR 設定時は使わない(no-color.org 慣習)。
const (
	ansiReset  = "\033[0m"
	ansiDim    = "\033[2m"
	ansiRed    = "\033[31m"
	ansiGreen  = "\033[32m"
	ansiYellow = "\033[33m"
	ansiCyan   = "\033[36m"
)

// colorEnabled は f が端末で、かつ NO_COLOR が未設定(空文字含む)のとき true。
// パイプ・リダイレクト・NO_COLOR 環境では装飾を行わずプレーン出力にする。
func colorEnabled(f *os.File) bool {
	if v := os.Getenv("NO_COLOR"); v != "" {
		return false
	}
	return isTerminal(f)
}

// styler は色付けの有無を保持し、条件付きで ANSI 装飾するヘルパ。
// on=false のときは素通し(同じ呼び出しでプレーン出力になる)。
type styler struct{ on bool }

func newStyler(on bool) styler { return styler{on: on} }

func (s styler) wrap(code, text string) string {
	if !s.on {
		return text
	}
	return code + text + ansiReset
}

func (s styler) green(t string) string  { return s.wrap(ansiGreen, t) }
func (s styler) yellow(t string) string { return s.wrap(ansiYellow, t) }
func (s styler) red(t string) string    { return s.wrap(ansiRed, t) }
func (s styler) cyan(t string) string   { return s.wrap(ansiCyan, t) }
func (s styler) dim(t string) string    { return s.wrap(ansiDim, t) }
