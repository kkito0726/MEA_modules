package usecase

import (
	"errors"
	"sync"
	"testing"
	"time"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

type fakeLister struct{ files []string }

func (f *fakeLister) List(root string, recursive bool) ([]string, error) { return f.files, nil }

type fakeReporter struct {
	mu                  sync.Mutex
	ok, skipped, failed int
}

func (r *fakeReporter) Begin(int)                  {}
func (r *fakeReporter) Done(string, time.Duration) { r.mu.Lock(); r.ok++; r.mu.Unlock() }
func (r *fakeReporter) Skipped(string, error)      { r.mu.Lock(); r.skipped++; r.mu.Unlock() }
func (r *fakeReporter) Failed(string, error)       { r.mu.Lock(); r.failed++; r.mu.Unlock() }
func (r *fakeReporter) Summary() (int, int, int) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.ok, r.skipped, r.failed
}

// fakeReader は入力名に応じて成功/バリデーション失敗/実行時失敗を返す。
type fakeReader struct{ name string }

func (r *fakeReader) Load(domain.TimeWindow) (domain.Measurement, error) {
	switch r.name {
	case "bad_validation":
		return domain.Measurement{}, &domain.ValidationError{Msg: "missing bio"}
	case "bad_runtime":
		return domain.Measurement{}, errors.New("disk error")
	default:
		return domain.Measurement{Voltages: [][]float32{{1}}, SamplingRate: 1}, nil
	}
}

type fakeWriter struct{}

func (fakeWriter) Write(domain.Measurement) error { return nil }

func TestBatch_SkipsValidationAndContinues(t *testing.T) {
	lister := &fakeLister{files: []string{"ok1", "bad_validation", "ok2", "bad_runtime", "ok3"}}
	reporter := &fakeReporter{}

	build := func(input, output string) (*ConvertUseCase, error) {
		return NewConvert(&fakeReader{name: input}, fakeWriter{}), nil
	}
	outputFor := func(input string) (string, error) { return input + ".npz", nil }

	batch := NewBatch(lister, reporter, build, outputFor, domain.TimeWindow{Full: true}, 2)
	if err := batch.Execute("root", false); err != nil {
		t.Fatalf("execute: %v", err)
	}

	ok, skipped, failed := reporter.Summary()
	if ok != 3 || skipped != 1 || failed != 1 {
		t.Errorf("ok=%d skipped=%d failed=%d, want 3/1/1", ok, skipped, failed)
	}
}

func TestBatch_OutputResolverError_CountedFailed(t *testing.T) {
	lister := &fakeLister{files: []string{"a", "b"}}
	reporter := &fakeReporter{}
	build := func(string, string) (*ConvertUseCase, error) {
		return NewConvert(&fakeReader{name: "ok"}, fakeWriter{}), nil
	}
	outputFor := func(input string) (string, error) {
		if input == "b" {
			return "", errors.New("cannot resolve")
		}
		return input + ".npz", nil
	}
	batch := NewBatch(lister, reporter, build, outputFor, domain.TimeWindow{Full: true}, 1)
	_ = batch.Execute("root", false)

	ok, _, failed := reporter.Summary()
	if ok != 1 || failed != 1 {
		t.Errorf("ok=%d failed=%d, want 1/1", ok, failed)
	}
}

// 並列でも全件処理されることの簡易確認
func TestBatch_ProcessesAll(t *testing.T) {
	var files []string
	for i := 0; i < 50; i++ {
		files = append(files, "ok"+string(rune('a'+i%26)))
	}
	lister := &fakeLister{files: files}
	reporter := &fakeReporter{}
	build := func(string, string) (*ConvertUseCase, error) {
		return NewConvert(&fakeReader{name: "ok"}, fakeWriter{}), nil
	}
	outputFor := func(input string) (string, error) { return input, nil }
	batch := NewBatch(lister, reporter, build, outputFor, domain.TimeWindow{Full: true}, 8)
	_ = batch.Execute("root", false)
	ok, _, _ := reporter.Summary()
	if ok != len(files) {
		t.Errorf("processed=%d, want %d", ok, len(files))
	}
}
