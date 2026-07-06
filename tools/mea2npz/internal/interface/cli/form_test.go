package cli

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

// 区間指定なし → 全区間・既定値が options に反映される。
func TestAssembleOptions_FullRange(t *testing.T) {
	o, code, ok := assembleOptions(formValues{
		input:        "/data/x.hed",
		dtypeStr:     "int16",
		specifyRange: false,
		distanceStr:  "450",
		resetTime:    true,
	})
	if !ok {
		t.Fatalf("assembleOptions 失敗 code=%d", code)
	}
	if !o.window.Full {
		t.Errorf("window=%+v, want Full", o.window)
	}
	if o.dtype != domain.DtypeInt16 || o.distance != 450 || !o.resetTime {
		t.Errorf("options=%+v", o)
	}
}

// 区間指定あり → start/end と各フラグが反映される。
func TestAssembleOptions_SpecifyRange(t *testing.T) {
	o, _, ok := assembleOptions(formValues{
		input:        "/data/x.hed",
		dtypeStr:     "float32",
		specifyRange: true,
		startStr:     "30",
		endStr:       "60",
		distanceStr:  "300",
		resetTime:    false,
		recursive:    true,
	})
	if !ok {
		t.Fatal("assembleOptions が失敗した")
	}
	if o.dtype != domain.DtypeFloat32 {
		t.Errorf("dtype=%s", o.dtype)
	}
	if o.window.Full || o.window.StartSec != 30 || o.window.EndSec != 60 {
		t.Errorf("window=%+v, want start30/end60", o.window)
	}
	if o.distance != 300 || o.resetTime || !o.recursive {
		t.Errorf("options=%+v", o)
	}
}

// 不正 dtype は code=2 で失敗する。
func TestAssembleOptions_InvalidDtype(t *testing.T) {
	_, code, ok := assembleOptions(formValues{input: "/x.hed", dtypeStr: "int8"})
	if ok || code != 2 {
		t.Errorf("不正 dtype は失敗(code=2): ok=%v code=%d", ok, code)
	}
}

// 不正な区間(start>=end)は code=2 で失敗する。
func TestAssembleOptions_InvalidRange(t *testing.T) {
	_, code, ok := assembleOptions(formValues{
		input:        "/x.hed",
		dtypeStr:     "int16",
		specifyRange: true,
		startStr:     "60",
		endStr:       "30",
	})
	if ok || code != 2 {
		t.Errorf("start>=end は失敗(code=2): ok=%v code=%d", ok, code)
	}
}

// 入力・出力の引用符はここでも除去される。
func TestAssembleOptions_UnquotesPaths(t *testing.T) {
	o, _, ok := assembleOptions(formValues{
		input:       "'/data/x.hed'",
		outPath:     `"/out/dir"`,
		dtypeStr:    "int16",
		distanceStr: "450",
	})
	if !ok {
		t.Fatal("assembleOptions が失敗した")
	}
	if o.input != "/data/x.hed" || o.out != "/out/dir" {
		t.Errorf("input=%q out=%q", o.input, o.out)
	}
}

func TestValidateInputPath(t *testing.T) {
	hed := filepath.Join(t.TempDir(), "data.hed")
	if err := os.WriteFile(hed, []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := validateInputPath(hed); err != nil {
		t.Errorf("既存パスはエラーにならないはず: %v", err)
	}
	if err := validateInputPath("'" + hed + "'"); err != nil {
		t.Errorf("引用符付き既存パスも通るはず: %v", err)
	}
	if err := validateInputPath("/no/such/path"); err == nil {
		t.Error("存在しないパスはエラーであるべき")
	}
	if err := validateInputPath(""); err == nil {
		t.Error("空文字はエラーであるべき")
	}
}

func TestYesNo(t *testing.T) {
	if yesNo(true) != "はい" || yesNo(false) != "いいえ" {
		t.Errorf("yesNo: true=%q false=%q", yesNo(true), yesNo(false))
	}
}

func TestValidateInt(t *testing.T) {
	if err := validateInt(" 42 "); err != nil {
		t.Errorf("整数はエラーにならないはず: %v", err)
	}
	if err := validateInt("abc"); err == nil {
		t.Error("非整数はエラーであるべき")
	}
}
