package cli

import (
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/infrastructure/npz"
	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/usecase"
)

// runInspect は .npz の計測メタ情報を表形式で表示する。
func runInspect(path string) int {
	info, err := usecase.NewInspect(npz.NewInfoReader(path)).Execute()
	if err != nil {
		reportError(os.Stderr, err)
		return 1
	}
	printInfoTable(os.Stdout, path, info, colorEnabled(os.Stdout))
	return 0
}

// printInfoTable はファイル情報を表で出力する。
func printInfoTable(w io.Writer, path string, info domain.MeasurementInfo, color bool) {
	dist := "N/A"
	if info.HasDistance {
		dist = strconv.Itoa(info.ElectrodeDistance)
	}
	rows := [][2]string{
		{"電極間距離 (um)", dist},
		{"サンプリングレート (Hz)", strconv.Itoa(info.SamplingRate)},
		{"GAIN", strconv.Itoa(info.Gain)},
		{"データ長 (s)", strconv.FormatFloat(info.DurationSec(), 'g', -1, 64)},
	}
	if info.Dtype != "" {
		rows = append(rows, [2]string{"dtype", info.Dtype})
	}

	fmt.Fprintf(w, "ファイル情報: %s\n", path)
	renderTable(w, [2]string{"項目", "値"}, rows, color)
}

// renderTable は CJK 幅を考慮して2列の Unicode 罫線テーブルを描画する。
// color=true のときヘッダ行を太字にする。
func renderTable(w io.Writer, header [2]string, rows [][2]string, color bool) {
	c0, c1 := dispWidth(header[0]), dispWidth(header[1])
	for _, r := range rows {
		if x := dispWidth(r[0]); x > c0 {
			c0 = x
		}
		if x := dispWidth(r[1]); x > c1 {
			c1 = x
		}
	}
	bar0, bar1 := strings.Repeat("─", c0+2), strings.Repeat("─", c1+2)
	fmt.Fprintf(w, "┌%s┬%s┐\n", bar0, bar1)
	fmt.Fprintf(w, "│ %s │ %s │\n", bold(pad(header[0], c0), color), bold(pad(header[1], c1), color))
	fmt.Fprintf(w, "├%s┼%s┤\n", bar0, bar1)
	for _, r := range rows {
		fmt.Fprintf(w, "│ %s │ %s │\n", pad(r[0], c0), pad(r[1], c1))
	}
	fmt.Fprintf(w, "└%s┴%s┘\n", bar0, bar1)
}

// bold は color=true のとき文字列を ANSI 太字で囲む(幅計算は囲む前に済ませる)。
func bold(s string, color bool) string {
	if color {
		return "\033[1m" + s + "\033[0m"
	}
	return s
}

func pad(s string, width int) string {
	if n := width - dispWidth(s); n > 0 {
		return s + strings.Repeat(" ", n)
	}
	return s
}

// dispWidth は端末表示幅を返す(全角=2, 半角=1)。
func dispWidth(s string) int {
	w := 0
	for _, r := range s {
		if isWide(r) {
			w += 2
		} else {
			w++
		}
	}
	return w
}

// isWide は East Asian Wide/Fullwidth に該当するか(日本語ラベルの整列用)。
func isWide(r rune) bool {
	switch {
	case r >= 0x1100 && r <= 0x115F: // Hangul Jamo
		return true
	case r >= 0x2E80 && r <= 0xA4CF: // CJK 部首〜記号/ひらがな/カタカナ/漢字 等
		return true
	case r >= 0xAC00 && r <= 0xD7A3: // Hangul 音節
		return true
	case r >= 0xF900 && r <= 0xFAFF: // CJK 互換漢字
		return true
	case r >= 0xFE30 && r <= 0xFE4F: // CJK 互換形
		return true
	case r >= 0xFF00 && r <= 0xFF60: // 全角形
		return true
	case r >= 0xFFE0 && r <= 0xFFE6: // 全角記号
		return true
	}
	return false
}
