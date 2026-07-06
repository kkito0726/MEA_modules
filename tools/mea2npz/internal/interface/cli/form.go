package cli

import (
	"errors"
	"fmt"
	"os"
	"runtime"
	"strconv"
	"strings"

	"github.com/charmbracelet/huh"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

// runForm は TTY 環境での対話モード。huh フォームで options を組み立てて dispatch する。
// 非 TTY 環境(パイプ・CI)では runInteractive(collectOptions) が使われ、こちらは呼ばれない。
func runForm() int {
	o, code, ok := collectOptionsForm()
	if !ok {
		return code
	}
	return dispatch(o)
}

// collectOptionsForm は huh フォームで対話的に options を組み立てる。
// 成功時は (options, 0, true)、中断は (zero, 130, false)、入力不正は (zero, 2, false)。
//
// 各項目は独立した単一フォームとして1問ずつ尋ねる。huh は完了時に自身の描画を消すため、
// 確定した回答は askForm が自前で1行印字して画面に残す(回答済みは残る・未回答は出さない)。
// 入力パスは Validate で存在確認し、失敗時はフォーム内で再入力を促す(プロセスは落とさない)。
func collectOptionsForm() (options, int, bool) {
	// 入力パス。存在するまでフォーム内で再入力を求める。
	var input string
	if err := askForm(
		"入力パス",
		huh.NewInput().
			Title("入力パス (.hed ファイル or ディレクトリ)").
			Description("ドラッグ&ドロップやコピー&ペーストで指定できます").
			Value(&input).
			Validate(validateInputPath),
		func() string { return unquotePath(input) },
	); err != nil {
		return abortForm(err)
	}
	input = unquotePath(input)
	info, err := os.Stat(input)
	if err != nil {
		// Validate を通過しているため通常は到達しないが、競合削除等の保険。
		fmt.Fprintln(os.Stderr, "エラー: 入力が見つかりません:", input)
		return options{}, 2, false
	}
	// .npz は情報表示モード。変換用の質問はしない。
	if !info.IsDir() && strings.HasSuffix(strings.ToLower(input), ".npz") {
		return options{input: input}, 0, true
	}

	// 保存 dtype。
	dtypeStr := "int16"
	if err := askForm(
		"保存 dtype",
		huh.NewSelect[string]().
			Title("保存 dtype").
			Options(
				huh.NewOption("int16 (既定・軽量)", "int16"),
				huh.NewOption("float32", "float32"),
			).
			Value(&dtypeStr),
		func() string { return dtypeStr },
	); err != nil {
		return abortForm(err)
	}

	// 読み込み時間の指定有無。
	specifyRange := true
	if err := askForm(
		"読み込み時間を指定する",
		huh.NewConfirm().Title("読み込み時間を指定する").Value(&specifyRange),
		func() string { return yesNo(specifyRange) },
	); err != nil {
		return abortForm(err)
	}

	// 区間(指定時のみ)。
	var startStr, endStr string
	if specifyRange {
		if err := askForm(
			"読込開始 (秒)",
			huh.NewInput().Title("読込開始 (秒)").Value(&startStr).Validate(validateInt),
			func() string { return strings.TrimSpace(startStr) + " 秒" },
		); err != nil {
			return abortForm(err)
		}
		if err := askForm(
			"読込終了 (秒)",
			huh.NewInput().Title("読込終了 (秒)").Value(&endStr).Validate(func(s string) error {
				end, err := strconv.Atoi(strings.TrimSpace(s))
				if err != nil {
					return errors.New("整数を入力してください")
				}
				start, _ := strconv.Atoi(strings.TrimSpace(startStr))
				if end <= start {
					return errors.New("終了は開始より大きくしてください")
				}
				return nil
			}),
			func() string { return strings.TrimSpace(endStr) + " 秒" },
		); err != nil {
			return abortForm(err)
		}
	}

	// 電極間距離。
	distanceStr := "450"
	if err := askForm(
		"電極間距離 (μm)",
		huh.NewInput().Title("電極間距離 (μm)").Value(&distanceStr).Validate(validateInt),
		func() string { return strings.TrimSpace(distanceStr) + " μm" },
	); err != nil {
		return abortForm(err)
	}

	// 時刻リセット。
	resetTime := true
	if err := askForm(
		"時刻を 0s にリセットする",
		huh.NewConfirm().Title("時刻を 0s にリセットする").Value(&resetTime),
		func() string { return yesNo(resetTime) },
	); err != nil {
		return abortForm(err)
	}

	// 出力先。
	var outPath string
	if err := askForm(
		"出力先",
		huh.NewInput().Title("出力先 (空で既定)").Value(&outPath),
		func() string {
			if strings.TrimSpace(outPath) == "" {
				return "(既定)"
			}
			return unquotePath(outPath)
		},
	); err != nil {
		return abortForm(err)
	}

	// 再帰探索(ディレクトリ入力のときのみ)。
	recursive := false
	if info.IsDir() {
		if err := askForm(
			"サブフォルダも探索する",
			huh.NewConfirm().Title("サブフォルダも探索する").Value(&recursive),
			func() string { return yesNo(recursive) },
		); err != nil {
			return abortForm(err)
		}
	}

	return assembleOptions(formValues{
		input:        input,
		dtypeStr:     dtypeStr,
		specifyRange: specifyRange,
		startStr:     startStr,
		endStr:       endStr,
		distanceStr:  distanceStr,
		resetTime:    resetTime,
		outPath:      outPath,
		recursive:    recursive,
	})
}

// askForm は単一項目のフォームを実行し、完了後に回答を transcript として1行残す。
// huh は完了時に自身の描画を消す(View が空を返す)ため、確定回答の表示は自前で行う。
func askForm(label string, field huh.Field, answer func() string) error {
	if err := huh.NewForm(huh.NewGroup(field)).Run(); err != nil {
		return err
	}
	echoAnswer(label, answer())
	return nil
}

// echoAnswer は確定した回答を「✓ ラベル: 値」の形で標準エラーへ残す。
func echoAnswer(label, value string) {
	st := newStyler(colorEnabled(os.Stderr))
	fmt.Fprintf(os.Stderr, "%s %s: %s\n", st.green("✓"), label, st.cyan(value))
}

// yesNo は Confirm の結果を transcript 表示用の日本語にする。
func yesNo(b bool) string {
	if b {
		return "はい"
	}
	return "いいえ"
}

// formValues はフォームで集めた生の入力値(文字列/真偽)。
// huh に依存せずテストできるよう、options への組み立てを assembleOptions に分離する。
type formValues struct {
	input        string
	dtypeStr     string
	specifyRange bool
	startStr     string
	endStr       string
	distanceStr  string
	resetTime    bool
	outPath      string
	recursive    bool
}

// assembleOptions はフォームの生入力を options に変換する(TTY 非依存の純粋ロジック)。
// dtype 不正や区間不正は (zero, 2, false) を返す。数値欄は Validate 済み前提だが、
// 空/非数は既定 0 として扱い panic しない。
func assembleOptions(v formValues) (options, int, bool) {
	dtype, err := domain.ParseDtype(v.dtypeStr)
	if err != nil {
		fmt.Fprintln(os.Stderr, "エラー:", err)
		return options{}, 2, false
	}

	var window domain.TimeWindow
	if v.specifyRange {
		start, _ := strconv.Atoi(strings.TrimSpace(v.startStr))
		end, _ := strconv.Atoi(strings.TrimSpace(v.endStr))
		window = domain.TimeWindow{StartSec: start, EndSec: end}
	} else {
		window = domain.TimeWindow{Full: true}
	}
	if err := window.Validate(); err != nil {
		fmt.Fprintln(os.Stderr, "エラー:", err)
		return options{}, 2, false
	}

	distance, _ := strconv.Atoi(strings.TrimSpace(v.distanceStr))

	return options{
		input:     unquotePath(v.input),
		out:       unquotePath(v.outPath),
		window:    window,
		dtype:     dtype,
		distance:  distance,
		resetTime: v.resetTime,
		recursive: v.recursive,
		jobs:      runtime.NumCPU(),
	}, 0, true
}

// validateInputPath は入力パスが存在するかを確認する(huh の Validate 用)。
// 引用符付きのコピペにも対応するため unquotePath を通してから判定する。
func validateInputPath(s string) error {
	s = unquotePath(s)
	if s == "" {
		return errors.New("パスを入力してください")
	}
	if _, err := os.Stat(s); err != nil {
		return fmt.Errorf("見つかりません: %s", s)
	}
	return nil
}

// validateInt は整数として解釈できるかを確認する(huh の Validate 用)。
func validateInt(s string) error {
	if _, err := strconv.Atoi(strings.TrimSpace(s)); err != nil {
		return errors.New("整数を入力してください")
	}
	return nil
}

// abortForm は huh の実行エラーを終了コードに変換する。
// Ctrl+C / Esc による中断は 130(SIGINT 慣習)、それ以外は 1。
func abortForm(err error) (options, int, bool) {
	if errors.Is(err, huh.ErrUserAborted) {
		fmt.Fprintln(os.Stderr, "中断しました。")
		return options{}, 130, false
	}
	fmt.Fprintln(os.Stderr, "エラー:", err)
	return options{}, 1, false
}
