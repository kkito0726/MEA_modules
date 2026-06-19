package cli

import (
	"fmt"
	"os"
	"sync"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/usecase"
)

// consoleReporter は usecase.ProgressReporter を標準エラー出力で実装する。
// 並列ジョブから呼ばれるためカウントを mutex で保護する。
type consoleReporter struct {
	mu      sync.Mutex
	ok      int
	skipped int
	failed  int
}

// コンパイル時に調停ポートの実装を強制する。
var _ usecase.ProgressReporter = (*consoleReporter)(nil)

func newConsoleReporter() *consoleReporter { return &consoleReporter{} }

func (r *consoleReporter) Done(path string) {
	r.mu.Lock()
	r.ok++
	r.mu.Unlock()
	fmt.Fprintln(os.Stderr, "[OK]  ", path)
}

func (r *consoleReporter) Skipped(path string, reason error) {
	r.mu.Lock()
	r.skipped++
	r.mu.Unlock()
	fmt.Fprintln(os.Stderr, "[SKIP]", path, "-", reason)
}

func (r *consoleReporter) Failed(path string, err error) {
	r.mu.Lock()
	r.failed++
	r.mu.Unlock()
	fmt.Fprintln(os.Stderr, "[FAIL]", path, "-", err)
}

func (r *consoleReporter) Summary() (ok, skipped, failed int) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.ok, r.skipped, r.failed
}
