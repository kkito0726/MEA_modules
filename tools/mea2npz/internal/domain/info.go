package domain

// MeasurementInfo は .npz から読み取る計測メタ情報(電位データ本体は含まない)。
type MeasurementInfo struct {
	SamplingRate      int
	Gain              int
	Start             float64
	End               float64
	ElectrodeDistance int
	HasDistance       bool // 旧形式(電極間距離なし)との後方互換
	Dtype             string
}

// DurationSec は計測時間(秒) = End - Start を返す。
func (i MeasurementInfo) DurationSec() float64 { return i.End - i.Start }

// MeasurementInfoReader は計測メタ情報の取得元を表すリポジトリポート。
// .npz 等の具体フォーマットは知らない(infrastructure が実装する)。
type MeasurementInfoReader interface {
	Info() (MeasurementInfo, error)
}
