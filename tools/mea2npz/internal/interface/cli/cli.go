// Package cli は CLI 引数の解析・対話入力と変換フローの起動(配線)を担う。
package cli

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/infrastructure/fs"
	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/infrastructure/hedbio"
	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/infrastructure/npz"
	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/usecase"
)

// Version はビルド時に -ldflags で差し替え可能。
var Version = "1.1.0"

// options は1回の変換実行に必要な設定。フラグ経路と対話経路の両方がこれを組み立てる。
type options struct {
	input     string
	out       string
	window    domain.TimeWindow
	dtype     domain.Dtype
	distance  int
	resetTime bool
	recursive bool
	jobs      int
}

// Run は CLI を実行し、終了コードを返す。
// 引数なしで呼ばれた場合は対話モードに入る。
func Run(args []string) int {
	if len(args) == 0 {
		printBanner(os.Stderr, colorEnabled(os.Stderr))
		return runInteractive(os.Stdin, os.Stderr)
	}

	fl := flag.NewFlagSet("mea2npz", flag.ContinueOnError)
	var (
		out       = fl.String("o", "", "出力先 (ファイル or ディレクトリ)")
		start     = fl.Int("start", 0, "読込開始 (秒)")
		end       = fl.Int("end", -1, "読込終了 (秒)。省略時はファイル全体")
		dtypeStr  = fl.String("dtype", "int16", "保存dtype (int16|float32)")
		distance  = fl.Int("distance", 450, "電極間距離 (μm)")
		keepTime  = fl.Bool("keep-time", false, "時刻オフセットを保持 (既定はリセットして0s始まり)")
		recursive = fl.Bool("recursive", false, "ディレクトリ入力時にサブフォルダも再帰探索")
		jobs      = fl.Int("jobs", runtime.NumCPU(), "一括変換の並列数")
		showVer   = fl.Bool("version", false, "バージョンを表示")
	)
	fl.Usage = func() {
		fmt.Fprintf(os.Stderr, "使い方: mea2npz [options] <input.hed | directory>\n")
		fmt.Fprintf(os.Stderr, "        mea2npz                 (引数なしで対話モード)\n\n")
		fmt.Fprintf(os.Stderr, ".hed/.bio を .npz へ変換します。ディレクトリ指定で配下を一括変換します。\n\n")
		fl.PrintDefaults()
	}
	if err := fl.Parse(args); err != nil {
		return 2
	}
	if *showVer {
		printVersion(os.Stdout)
		return 0
	}

	printBanner(os.Stderr, colorEnabled(os.Stderr))

	if fl.NArg() != 1 {
		fmt.Fprintln(os.Stderr, "エラー: 入力 (.hed ファイル or ディレクトリ) を1つ指定してください")
		fl.Usage()
		return 2
	}

	dtype, err := domain.ParseDtype(*dtypeStr)
	if err != nil {
		fmt.Fprintln(os.Stderr, "エラー:", err)
		return 2
	}

	window := domain.TimeWindow{StartSec: *start}
	if *end < 0 {
		window.Full = true
	} else {
		window.EndSec = *end
	}
	if err := window.Validate(); err != nil {
		fmt.Fprintln(os.Stderr, "エラー:", err)
		return 2
	}

	return dispatch(options{
		input:     unquotePath(fl.Arg(0)),
		out:       unquotePath(*out),
		window:    window,
		dtype:     dtype,
		distance:  *distance,
		resetTime: !*keepTime,
		recursive: *recursive,
		jobs:      *jobs,
	})
}

// unquotePath は Finder やエクスプローラからコピー&ペーストした際に付く
// 引用符を取り除く。両端が同じ引用符 (' または ") で囲まれている場合のみ外す。
// 例: '/Volumes/Extreme SSD/data/230411' → /Volumes/Extreme SSD/data/230411
func unquotePath(s string) string {
	s = strings.TrimSpace(s)
	if len(s) >= 2 {
		q := s[0]
		if (q == '\'' || q == '"') && s[len(s)-1] == q {
			return s[1 : len(s)-1]
		}
	}
	return s
}

// dispatch は入力の種別で振り分ける。
// ディレクトリ → 一括変換 / .npz → 情報表示 / .hed → 単一変換。
func dispatch(o options) int {
	info, err := os.Stat(o.input)
	if err != nil {
		reportError(os.Stderr, fmt.Errorf("入力が見つかりません: %s", o.input))
		return 2
	}
	if info.IsDir() {
		return runBatch(o)
	}
	if strings.HasSuffix(strings.ToLower(o.input), ".npz") {
		return runInspect(o.input)
	}
	return runSingle(o)
}

// runSingle は単一 .hed を変換する。バリデーション失敗時は非0で終了する。
func runSingle(o options) int {
	if !strings.HasSuffix(strings.ToLower(o.input), ".hed") {
		fmt.Fprintln(os.Stderr, "エラー: 入力は .hed ファイルである必要があります:", o.input)
		return 2
	}

	outPath := resolveSingleOutput(o.input, o.out)
	st := newStyler(colorEnabled(os.Stdout))

	// 大きいファイルは読込・保存に時間がかかるため、開始を明示して利用者を安心させる。
	fmt.Printf("%s 変換開始\n", st.cyan("▶"))
	fmt.Printf("   入力: %s\n", o.input)
	fmt.Printf("   出力: %s\n", outPath)

	conv := usecase.NewConvert(
		hedbio.NewReader(o.input),
		npz.NewWriter(outPath, o.dtype, o.distance, o.resetTime, o.input),
	)
	start := time.Now()
	m, err := conv.Execute(o.window)
	if err != nil {
		reportError(os.Stderr, err)
		return 1
	}
	fmt.Printf("\n%s 変換完了  %s\n", st.green("✓"), st.dim(fmtDur(time.Since(start))))
	// 実際に保存した区間の情報を表示する(.npz の情報表示と一致する)。
	printInfoTable(os.Stdout, o.input, m.Info(o.distance, o.dtype), colorEnabled(os.Stdout))
	return 0
}

// runBatch はディレクトリ配下を一括変換する。スキップ/失敗があれば非0で終了する。
func runBatch(o options) int {
	outRoot := o.out
	if outRoot == "" {
		outRoot = filepath.Join(o.input, "output")
	}

	lister := fs.NewLister()
	reporter := newConsoleReporter(colorEnabled(os.Stderr))

	build := func(input, output string) (*usecase.ConvertUseCase, error) {
		return usecase.NewConvert(
			hedbio.NewReader(input),
			npz.NewWriter(output, o.dtype, o.distance, o.resetTime, input),
		), nil
	}
	outputFor := func(input string) (string, error) {
		rel, err := filepath.Rel(o.input, input)
		if err != nil {
			rel = filepath.Base(input)
		}
		rel = strings.TrimSuffix(rel, filepath.Ext(rel)) + ".npz"
		return filepath.Join(outRoot, rel), nil
	}

	batch := usecase.NewBatch(lister, reporter, build, outputFor, o.window, o.jobs)
	start := time.Now()
	if err := batch.Execute(o.input, o.recursive); err != nil {
		reportError(os.Stderr, err)
		return 1
	}

	ok, skipped, failed := reporter.Summary()
	printSummary(os.Stdout, newStyler(colorEnabled(os.Stdout)), ok, skipped, failed, time.Since(start), outRoot)
	if skipped+failed > 0 {
		return 1
	}
	return 0
}

// resolveSingleOutput は単一変換の出力パスを決める。
// out 未指定なら入力と同名 .npz、out が既存ディレクトリならその配下、それ以外は out をファイルパスとして扱う。
func resolveSingleOutput(input, out string) string {
	if out == "" {
		return strings.TrimSuffix(input, filepath.Ext(input)) + ".npz"
	}
	if info, err := os.Stat(out); err == nil && info.IsDir() {
		base := strings.TrimSuffix(filepath.Base(input), filepath.Ext(input)) + ".npz"
		return filepath.Join(out, base)
	}
	return out
}
