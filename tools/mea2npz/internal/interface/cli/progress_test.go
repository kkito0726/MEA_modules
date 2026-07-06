package cli

import (
	"bytes"
	"errors"
	"strings"
	"testing"
	"time"
)

// TTY かつ色付き可能ならバー、それ以外はカウンタ表示を選ぶ。
func TestNewBatchReporter_Selection(t *testing.T) {
	cases := []struct {
		name        string
		interactive bool
		color       bool
		wantBar     bool
	}{
		{"TTY+色 → バー", true, true, true},
		{"TTY+色なし(NO_COLOR) → カウンタ", true, false, false},
		{"非TTY → カウンタ", false, true, false},
		{"非TTY+色なし → カウンタ", false, false, false},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			r := newBatchReporter(&bytes.Buffer{}, c.interactive, c.color)
			_, isBar := r.(*barReporter)
			if isBar != c.wantBar {
				t.Errorf("bar=%v, want %v", isBar, c.wantBar)
			}
		})
	}
}

// barReporter は成功/スキップ/失敗を集計し、結果行を出力する。
func TestBarReporter_CountsAndOutput(t *testing.T) {
	var buf bytes.Buffer
	r := newBarReporter(&buf, false) // color=false でANSI装飾を避け検証しやすくする
	r.Begin(3)
	r.Done("/data/a.hed", 12*time.Millisecond)
	r.Skipped("/data/b.hed", errors.New(".bio が見つかりません"))
	r.Failed("/data/c.hed", errors.New("壊れています"))
	r.finish()

	ok, skipped, failed := r.Summary()
	if ok != 1 || skipped != 1 || failed != 1 {
		t.Errorf("counts = (%d,%d,%d), want (1,1,1)", ok, skipped, failed)
	}
	out := buf.String()
	for _, want := range []string{"全 3 件", "a.hed", "b.hed", "c.hed", "3/3"} {
		if !strings.Contains(out, want) {
			t.Errorf("出力に %q が含まれていない\n---\n%s", want, out)
		}
	}
	// スキップ理由に紐づくヒントが添えられる。
	if !strings.Contains(out, "ヒント:") {
		t.Errorf("スキップ時のヒントが出ていない\n---\n%s", out)
	}
}
