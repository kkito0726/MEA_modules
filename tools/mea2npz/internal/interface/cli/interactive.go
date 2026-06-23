package cli

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"runtime"
	"strconv"
	"strings"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

// runInteractive は引数なし起動時の対話モード。in から入力を読み、out へプロンプトを出す。
func runInteractive(in io.Reader, out io.Writer) int {
	o, code, ok := collectOptions(in, out)
	if !ok {
		return code
	}
	return dispatch(o)
}

// collectOptions は対話で options を組み立てる。
// 成功時は (options, 0, true)、中断/エラー時は (zero, code, false) を返す(dispatch と分離してテスト可能にする)。
func collectOptions(in io.Reader, out io.Writer) (options, int, bool) {
	r := bufio.NewReader(in)
	fmt.Fprintln(out, "mea2npz 対話モード — 各項目は Enter で既定値を採用します。")

	input, ok := promptRequired(r, out, "入力パス (.hed ファイル or ディレクトリ)")
	if !ok {
		fmt.Fprintln(out, "入力がありませんでした。終了します。")
		return options{}, 2, false
	}
	input = unquotePath(input)
	info, err := os.Stat(input)
	if err != nil {
		fmt.Fprintln(out, "エラー: 入力が見つかりません:", input)
		return options{}, 2, false
	}
	// .npz が渡された場合は情報表示モード。変換用の質問はしない。
	if !info.IsDir() && strings.HasSuffix(strings.ToLower(input), ".npz") {
		return options{input: input}, 0, true
	}

	dtypeStr := promptDefault(r, out, "保存dtype (int16/float32)", "int16")
	dtype, err := domain.ParseDtype(dtypeStr)
	if err != nil {
		fmt.Fprintln(out, "エラー:", err)
		return options{}, 2, false
	}

	var window domain.TimeWindow
	if promptYesNo(r, out, "読み込み時間を指定する", true) {
		start, ok := promptIntRequired(r, out, "読込開始 (秒)")
		if !ok {
			fmt.Fprintln(out, "入力が中断されました。終了します。")
			return options{}, 2, false
		}
		end, ok := promptIntRequired(r, out, "読込終了 (秒)")
		if !ok {
			fmt.Fprintln(out, "入力が中断されました。終了します。")
			return options{}, 2, false
		}
		window = domain.TimeWindow{StartSec: start, EndSec: end}
	} else {
		window = domain.TimeWindow{Full: true}
	}
	if err := window.Validate(); err != nil {
		fmt.Fprintln(out, "エラー:", err)
		return options{}, 2, false
	}

	distance := promptInt(r, out, "電極間距離 (μm)", 450)
	resetTime := promptYesNo(r, out, "時刻を 0s にリセットする", true)
	outPath := unquotePath(promptDefault(r, out, "出力先 — 空で既定", ""))

	recursive := false
	if info.IsDir() {
		recursive = promptYesNo(r, out, "サブフォルダも探索する", false)
	}

	return options{
		input:     input,
		out:       outPath,
		window:    window,
		dtype:     dtype,
		distance:  distance,
		resetTime: resetTime,
		recursive: recursive,
		jobs:      runtime.NumCPU(),
	}, 0, true
}

// readLine は1行読む。EOF かつ未読データなしのとき ok=false。
func readLine(r *bufio.Reader) (string, bool) {
	s, err := r.ReadString('\n')
	if err != nil && s == "" {
		return "", false
	}
	return strings.TrimRight(s, "\r\n"), true
}

// promptRequired は空でない値を得るまで繰り返す。EOF で ok=false。
func promptRequired(r *bufio.Reader, out io.Writer, label string) (string, bool) {
	for {
		fmt.Fprintf(out, "%s: ", label)
		s, ok := readLine(r)
		if !ok {
			return "", false
		}
		if s = strings.TrimSpace(s); s != "" {
			return s, true
		}
		fmt.Fprintln(out, "値を入力してください。")
	}
}

// promptDefault は空入力で既定値を返す。
func promptDefault(r *bufio.Reader, out io.Writer, label, def string) string {
	if def == "" {
		fmt.Fprintf(out, "%s: ", label)
	} else {
		fmt.Fprintf(out, "%s [%s]: ", label, def)
	}
	s, ok := readLine(r)
	if !ok {
		return def
	}
	if s = strings.TrimSpace(s); s == "" {
		return def
	}
	return s
}

// promptIntRequired は整数の入力を必須とする(既定値なし)。空入力は再入力を促し、EOF で ok=false。
func promptIntRequired(r *bufio.Reader, out io.Writer, label string) (int, bool) {
	for {
		fmt.Fprintf(out, "%s: ", label)
		s, ok := readLine(r)
		if !ok {
			return 0, false
		}
		if s = strings.TrimSpace(s); s == "" {
			fmt.Fprintln(out, "値を入力してください。")
			continue
		}
		if v, err := strconv.Atoi(s); err == nil {
			return v, true
		}
		fmt.Fprintln(out, "整数を入力してください。")
	}
}

// promptInt は整数を得るまで繰り返す。空入力/EOF で既定値。
func promptInt(r *bufio.Reader, out io.Writer, label string, def int) int {
	for {
		fmt.Fprintf(out, "%s [%d]: ", label, def)
		s, ok := readLine(r)
		if !ok {
			return def
		}
		if s = strings.TrimSpace(s); s == "" {
			return def
		}
		if v, err := strconv.Atoi(s); err == nil {
			return v
		}
		fmt.Fprintln(out, "整数を入力してください。")
	}
}

// promptYesNo は y/n を得るまで繰り返す。空入力/EOF で既定値。
func promptYesNo(r *bufio.Reader, out io.Writer, label string, def bool) bool {
	hint := "y/N"
	if def {
		hint = "Y/n"
	}
	for {
		fmt.Fprintf(out, "%s [%s]: ", label, hint)
		s, ok := readLine(r)
		if !ok {
			return def
		}
		switch strings.ToLower(strings.TrimSpace(s)) {
		case "":
			return def
		case "y", "yes":
			return true
		case "n", "no":
			return false
		}
		fmt.Fprintln(out, "y または n を入力してください。")
	}
}
