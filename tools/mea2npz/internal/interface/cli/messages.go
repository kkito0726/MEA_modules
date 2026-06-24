package cli

import (
	"fmt"
	"io"
	"os"
	"strings"
	"time"
)

// hintFor はエラー文言から初心者向けの対処ヒントを返す(該当なしは空文字)。
// ドメインのエラー型に依存せず、利用者向けの案内はプレゼンテーション層で持つ(文言マッチの best-effort)。
func hintFor(err error) string {
	if err == nil {
		return ""
	}
	msg := err.Error()
	switch {
	case strings.Contains(msg, "入力が見つかりません"):
		return "パスのつづりが正しいか、ファイル/フォルダが存在するか確認してください"
	case strings.Contains(msg, ".bio が見つかりません"):
		return ".hed と同じフォルダに「<ファイル名>0001.bio」があるか確認してください"
	case strings.Contains(msg, ".hed を読み込めません"), strings.Contains(msg, ".hed が短すぎます"):
		return ".hed ファイルが壊れていないか、正しい計測ファイルか確認してください"
	case strings.Contains(msg, "未知のGAIN"), strings.Contains(msg, "未知のサンプリングレート"):
		return "この .hed は対応外の設定です。別の計測ファイルで試してください"
	case strings.Contains(msg, "データ長を超えています"), strings.Contains(msg, "読み込む区間が空です"):
		return "-start / -end の秒数がデータ長の範囲内か確認してください"
	case strings.Contains(msg, "がありません(非対応の形式)"):
		return "pyMEA で保存した .npz か確認してください"
	case strings.Contains(msg, "dtype は"):
		return "-dtype には int16 か float32 を指定してください"
	}
	return ""
}

// reportError はエラーを赤字で表示し、対処ヒントがあれば添える。
func reportError(f *os.File, err error) {
	st := newStyler(colorEnabled(f))
	fmt.Fprintln(f, st.red("✗ エラー:"), err)
	if h := hintFor(err); h != "" {
		fmt.Fprintf(f, "   %s %s\n", st.dim("↳ ヒント:"), h)
	}
}

// printSummary は一括変換の結果を枠付きで表示する(成功=緑/スキップ=黄/失敗=赤)。
func printSummary(w io.Writer, st styler, ok, skipped, failed int, elapsed time.Duration, outRoot string) {
	line := strings.Repeat("─", 48)
	fmt.Fprintf(w, "\n%s\n", line)
	fmt.Fprintf(w, "  %s    %s    %s    %s\n",
		st.green(fmt.Sprintf("成功 %d", ok)),
		st.yellow(fmt.Sprintf("スキップ %d", skipped)),
		st.red(fmt.Sprintf("失敗 %d", failed)),
		st.dim("所要 "+fmtDur(elapsed)),
	)
	fmt.Fprintf(w, "  出力先: %s\n", outRoot)
	fmt.Fprintf(w, "%s\n", line)
}

// fmtDur は所要時間を読みやすい表記にする(1秒未満は ms、それ以上は秒)。
func fmtDur(d time.Duration) string {
	if d < time.Second {
		return fmt.Sprintf("%dms", d.Milliseconds())
	}
	return fmt.Sprintf("%.1fs", d.Seconds())
}
