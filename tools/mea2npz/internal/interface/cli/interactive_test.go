package cli

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

func tempHed(t *testing.T) string {
	t.Helper()
	hed := filepath.Join(t.TempDir(), "data.hed")
	if err := os.WriteFile(hed, []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	return hed
}

func script(lines ...string) string {
	return strings.Join(lines, "\n") + "\n"
}

// 時間指定なし(n)→ 全区間。他は既定。
func TestCollectOptions_FullRange(t *testing.T) {
	hed := tempHed(t)
	in := script(
		hed, // 入力
		"",  // dtype 既定 int16
		"n", // 読み込み時間を指定する → no
		"",  // 電極間距離 既定 450
		"",  // 時刻リセット 既定 Y
		"",  // 出力先 既定
	)
	o, code, ok := collectOptions(strings.NewReader(in), &bytes.Buffer{})
	if !ok {
		t.Fatalf("collectOptions 失敗 code=%d", code)
	}
	if o.dtype != domain.DtypeInt16 {
		t.Errorf("dtype=%s", o.dtype)
	}
	if !o.window.Full {
		t.Errorf("window=%+v, want Full", o.window)
	}
	if o.distance != 450 || !o.resetTime {
		t.Errorf("distance=%d resetTime=%v", o.distance, o.resetTime)
	}
}

// 時間指定あり(y)→ start/end を必須で受け取る。
func TestCollectOptions_SpecifyRange(t *testing.T) {
	hed := tempHed(t)
	in := script(
		hed,       // 入力
		"float32", // dtype
		"y",       // 読み込み時間を指定する → yes
		"30",      // start(必須)
		"60",      // end(必須)
		"300",     // 電極間距離
		"n",       // 時刻リセット → no(keep-time)
		"",        // 出力先 既定
	)
	o, code, ok := collectOptions(strings.NewReader(in), &bytes.Buffer{})
	if !ok {
		t.Fatalf("collectOptions 失敗 code=%d", code)
	}
	if o.dtype != domain.DtypeFloat32 {
		t.Errorf("dtype=%s", o.dtype)
	}
	if o.window.Full || o.window.StartSec != 30 || o.window.EndSec != 60 {
		t.Errorf("window=%+v, want start30/end60", o.window)
	}
	if o.distance != 300 || o.resetTime {
		t.Errorf("distance=%d resetTime=%v", o.distance, o.resetTime)
	}
}

// 既定(空入力)で時間指定=Yes となり、start/end の入力を促す。
func TestCollectOptions_SpecifyRange_DefaultYes(t *testing.T) {
	hed := tempHed(t)
	in := script(
		hed,  // 入力
		"",   // dtype 既定
		"",   // 読み込み時間を指定する → 既定 Yes
		"10", // start
		"20", // end
		"",   // 距離 既定
		"",   // リセット 既定
		"",   // 出力 既定
	)
	o, _, ok := collectOptions(strings.NewReader(in), &bytes.Buffer{})
	if !ok || o.window.Full || o.window.StartSec != 10 || o.window.EndSec != 20 {
		t.Errorf("ok=%v window=%+v, want start10/end20", ok, o.window)
	}
}

// 不正な区間(start>=end)はバリデーションで失敗する。
func TestCollectOptions_InvalidRange(t *testing.T) {
	hed := tempHed(t)
	in := script(hed, "", "y", "60", "30")
	_, code, ok := collectOptions(strings.NewReader(in), &bytes.Buffer{})
	if ok || code != 2 {
		t.Errorf("start>=end は失敗(code=2)であるべき: ok=%v code=%d", ok, code)
	}
}

// start 必須入力中の EOF は中断。
func TestCollectOptions_AbortOnRequiredStartEOF(t *testing.T) {
	hed := tempHed(t)
	in := script(hed, "", "y") // start を入れずに終端
	_, code, ok := collectOptions(strings.NewReader(in), &bytes.Buffer{})
	if ok || code != 2 {
		t.Errorf("start 未入力(EOF)は中断(code=2)であるべき: ok=%v code=%d", ok, code)
	}
}

func TestCollectOptions_DirAsksRecursive(t *testing.T) {
	dir := t.TempDir()
	in := script(
		dir, // 入力(ディレクトリ)
		"",  // dtype
		"n", // 時間指定なし
		"",  // 距離
		"",  // リセット
		"",  // 出力
		"y", // サブフォルダ探索
	)
	o, code, ok := collectOptions(strings.NewReader(in), &bytes.Buffer{})
	if !ok {
		t.Fatalf("collectOptions 失敗 code=%d", code)
	}
	if !o.recursive {
		t.Errorf("recursive=y が反映されていない")
	}
}

func TestCollectOptions_MissingInput(t *testing.T) {
	_, code, ok := collectOptions(strings.NewReader("/no/such/path.hed\n"), &bytes.Buffer{})
	if ok || code != 2 {
		t.Errorf("存在しない入力は失敗(code=2): ok=%v code=%d", ok, code)
	}
}

func TestCollectOptions_EmptyInputAborts(t *testing.T) {
	_, code, ok := collectOptions(strings.NewReader(""), &bytes.Buffer{})
	if ok || code != 2 {
		t.Errorf("入力なしは中断(code=2): ok=%v code=%d", ok, code)
	}
}
