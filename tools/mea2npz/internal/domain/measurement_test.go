package domain

import "testing"

// 時間窓を指定した計測データの Info は、ファイル全体ではなく
// 実際に保持している区間のデータ長 (End-Start) を返す。
func TestMeasurementInfo_ReflectsWindow(t *testing.T) {
	m := Measurement{
		Voltages:     make([][]float32, 64),
		SamplingRate: 10000,
		Gain:         2000,
		Start:        30,
		End:          60,
	}
	info := m.Info(450, DtypeInt16)

	if got := info.DurationSec(); got != 30 {
		t.Errorf("DurationSec()=%v, want 30 (= End-Start, 窓の長さ)", got)
	}
	if info.SamplingRate != 10000 || info.Gain != 2000 {
		t.Errorf("sr=%d gain=%d", info.SamplingRate, info.Gain)
	}
	if info.ElectrodeDistance != 450 || !info.HasDistance {
		t.Errorf("distance=%d hasDistance=%v", info.ElectrodeDistance, info.HasDistance)
	}
	if info.Dtype != "int16" {
		t.Errorf("dtype=%q, want int16", info.Dtype)
	}
}

// 電極間距離が 0 (未指定) のとき HasDistance は false。
func TestMeasurementInfo_NoDistance(t *testing.T) {
	info := Measurement{}.Info(0, DtypeFloat32)
	if info.HasDistance {
		t.Errorf("distance=0 のとき HasDistance は false であるべき")
	}
}
