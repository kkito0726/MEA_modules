package domain

import "fmt"

// ValidationError は入力バリデーション由来のエラー。
// 一括変換では実行時エラーと区別し「スキップ(継続)」扱いにするためのマーカー。
type ValidationError struct {
	Msg string
}

func (e *ValidationError) Error() string { return e.Msg }

// TimeWindow は読み込む時間窓(秒)を表す値オブジェクト。
// Full=true のときは StartSec からファイル終端まで全区間を読む(EndSec は無視)。
type TimeWindow struct {
	StartSec int
	EndSec   int
	Full     bool
}

// Validate は時間窓の整合性を検証する。
func (w TimeWindow) Validate() error {
	if w.StartSec < 0 {
		return &ValidationError{Msg: fmt.Sprintf("start は 0 以上である必要があります: %d", w.StartSec)}
	}
	if !w.Full && w.EndSec <= w.StartSec {
		return &ValidationError{Msg: fmt.Sprintf("end (%d) は start (%d) より大きい必要があります", w.EndSec, w.StartSec)}
	}
	return nil
}

// Dtype は保存時の量子化形式を表す値オブジェクト。
type Dtype string

const (
	DtypeInt16   Dtype = "int16"
	DtypeFloat32 Dtype = "float32"
)

// ParseDtype は文字列から Dtype を生成する。
func ParseDtype(s string) (Dtype, error) {
	switch s {
	case string(DtypeInt16):
		return DtypeInt16, nil
	case string(DtypeFloat32):
		return DtypeFloat32, nil
	default:
		return "", &ValidationError{Msg: fmt.Sprintf("dtype は int16 または float32 を指定してください: %s", s)}
	}
}
