package cli

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/usecase"
)

// consoleReporter は usecase.ProgressReporter を標準エラー出力で実装する。
// 並列ジョブから呼ばれるためカウントを mutex で保護する。色付け・進捗カウンタ・所要時間を表示する。
type consoleReporter struct {
	mu      sync.Mutex
	st      styler
	total   int
	ok      int
	skipped int
	failed  int
}

// コンパイル時に調停ポートの実装を強制する。
var _ usecase.ProgressReporter = (*consoleReporter)(nil)

func newConsoleReporter(color bool) *consoleReporter {
	return &consoleReporter{st: newStyler(color)}
}

// Begin は並列処理開始前に1回だけ呼ばれる(まだ goroutine は走っていない)。
func (r *consoleReporter) Begin(total int) {
	r.total = total
	fmt.Fprintf(os.Stderr, "%s 全 %d 件を変換します\n\n", r.st.cyan("▶"), total)
}

// counter は "[n/総数]" を淡色で返す(進捗の見える化)。
func (r *consoleReporter) counter(n int) string {
	return r.st.dim(fmt.Sprintf("[%d/%d]", n, r.total))
}

func (r *consoleReporter) Done(path string, elapsed time.Duration) {
	r.mu.Lock()
	r.ok++
	n := r.ok + r.skipped + r.failed
	r.mu.Unlock()
	fmt.Fprintf(os.Stderr, "  %s %s %s  %s\n",
		r.st.green("✓"), r.counter(n), filepath.Base(path), r.st.dim(fmtDur(elapsed)))
}

func (r *consoleReporter) Skipped(path string, reason error) {
	r.mu.Lock()
	r.skipped++
	n := r.ok + r.skipped + r.failed
	r.mu.Unlock()
	fmt.Fprintf(os.Stderr, "  %s %s %s — %s\n",
		r.st.yellow("⚠"), r.counter(n), filepath.Base(path), reason)
	if h := hintFor(reason); h != "" {
		fmt.Fprintf(os.Stderr, "     %s %s\n", r.st.dim("↳ ヒント:"), h)
	}
}

func (r *consoleReporter) Failed(path string, err error) {
	r.mu.Lock()
	r.failed++
	n := r.ok + r.skipped + r.failed
	r.mu.Unlock()
	fmt.Fprintf(os.Stderr, "  %s %s %s — %s\n",
		r.st.red("✗"), r.counter(n), filepath.Base(path), err)
	if h := hintFor(err); h != "" {
		fmt.Fprintf(os.Stderr, "     %s %s\n", r.st.dim("↳ ヒント:"), h)
	}
}

func (r *consoleReporter) Summary() (ok, skipped, failed int) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.ok, r.skipped, r.failed
}
