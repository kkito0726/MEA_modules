package cli

import (
	"fmt"
	"io"
	"path/filepath"
	"sync"
	"time"

	"github.com/charmbracelet/bubbles/progress"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/usecase"
)

// barReporter は一括変換の進捗をプログレスバーで表示する batchReporter 実装。
// 各ファイルの結果行は上へ流し、最下段に「全体バー + n/総数」を居座らせて随時更新する。
// bubbletea のイベントループは使わず、bubbles/progress のレンダリング(ViewAs)と
// キャリッジリターン(\r)によるインプレース更新で実現する(並列ジョブとの協調が単純になる)。
type barReporter struct {
	mu      sync.Mutex
	st      styler
	bar     progress.Model
	w       io.Writer
	total   int
	ok      int
	skipped int
	failed  int
}

var _ batchReporter = (*barReporter)(nil)

// clearLine はカーソル行頭復帰 + 行末まで消去する ANSI シーケンス(バー行の消去用)。
const clearLine = "\r\033[K"

func newBarReporter(w io.Writer, color bool) *barReporter {
	return &barReporter{
		st:  newStyler(color),
		bar: progress.New(progress.WithWidth(30), progress.WithDefaultGradient()),
		w:   w,
	}
}

// Begin は総数を確定し、ヘッダと初期バーを表示する(goroutine 起動前に1回)。
func (r *barReporter) Begin(total int) {
	r.total = total
	fmt.Fprintf(r.w, "%s 全 %d 件を変換します\n\n", r.st.cyan("▶"), total)
	fmt.Fprint(r.w, r.barLine())
}

func (r *barReporter) Done(path string, elapsed time.Duration) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.ok++
	r.emit(fmt.Sprintf("  %s %s %s  %s",
		r.st.green("✓"), r.counter(), filepath.Base(path), r.st.dim(fmtDur(elapsed))))
}

func (r *barReporter) Skipped(path string, reason error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.skipped++
	r.emit(r.resultWithHint(r.st.yellow("⚠"), path, reason)...)
}

func (r *barReporter) Failed(path string, err error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.failed++
	r.emit(r.resultWithHint(r.st.red("✗"), path, err)...)
}

func (r *barReporter) Summary() (ok, skipped, failed int) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.ok, r.skipped, r.failed
}

// finish はバー行を確定表示して改行し、後続の printSummary が崩れないようにする。
func (r *barReporter) finish() {
	r.mu.Lock()
	defer r.mu.Unlock()
	fmt.Fprint(r.w, clearLine)
	fmt.Fprintln(r.w, r.barLine())
}

// resultWithHint は結果行と(あれば)ヒント行を組み立てる。
func (r *barReporter) resultWithHint(mark, path string, reason error) []string {
	lines := []string{fmt.Sprintf("  %s %s %s — %s",
		mark, r.counter(), filepath.Base(path), reason)}
	if h := hintFor(reason); h != "" {
		lines = append(lines, fmt.Sprintf("     %s %s", r.st.dim("↳ ヒント:"), h))
	}
	return lines
}

// emit はバー行を消去し、結果行を流してからバーを再描画する(要ロック)。
func (r *barReporter) emit(lines ...string) {
	fmt.Fprint(r.w, clearLine)
	for _, l := range lines {
		fmt.Fprintln(r.w, l)
	}
	fmt.Fprint(r.w, r.barLine())
}

// counter は "[n/総数]" を淡色で返す(要ロック)。
func (r *barReporter) counter() string {
	n := r.ok + r.skipped + r.failed
	return r.st.dim(fmt.Sprintf("[%d/%d]", n, r.total))
}

// barLine は「バー + n/総数」の1行を返す(要ロック)。
func (r *barReporter) barLine() string {
	n := r.ok + r.skipped + r.failed
	frac := 0.0
	if r.total > 0 {
		frac = float64(n) / float64(r.total)
	}
	return fmt.Sprintf("%s  %s", r.bar.ViewAs(frac), r.st.dim(fmt.Sprintf("%d/%d", n, r.total)))
}

// newBatchReporter は環境に応じた batchReporter を選ぶ。
// TTY かつ色付き可能ならプログレスバー、そうでなければ行ベースのカウンタ表示。
func newBatchReporter(w io.Writer, interactive, color bool) batchReporter {
	if interactive && color {
		return newBarReporter(w, color)
	}
	return newConsoleReporter(color)
}

// コンパイル時に usecase 側のポート実装であることを保証する。
var _ usecase.ProgressReporter = (*barReporter)(nil)
