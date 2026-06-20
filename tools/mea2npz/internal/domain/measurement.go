// Package domain は計測データのエンティティ・値オブジェクト・ドメインサービス・
// リポジトリポートを提供する最内レイヤー。外部I/O・フォーマットに一切依存しない。
package domain

// Measurement は MEA 計測データのイミュータブルな集約。
// Voltages は電極ごと(64ch)×サンプル数(N)の電位データ(float32保持)。
// Start/End は計測データが対応する時間窓(秒)。
type Measurement struct {
	Voltages     [][]float32
	SamplingRate int
	Gain         int
	Start        float64
	End          float64
}

// Info は実際に保持している計測区間のメタ情報を返す(表示用)。
// Start/End は読み込んだ時間窓を反映するため、.npz 保存後の情報表示と一致する。
func (m Measurement) Info(distance int, dtype Dtype) MeasurementInfo {
	return MeasurementInfo{
		SamplingRate:      m.SamplingRate,
		Gain:              m.Gain,
		Start:             m.Start,
		End:               m.End,
		ElectrodeDistance: distance,
		HasDistance:       distance > 0,
		Dtype:             string(dtype),
	}
}

// Channels は電極数を返す。
func (m Measurement) Channels() int { return len(m.Voltages) }

// Samples はサンプル数(N)を返す。
func (m Measurement) Samples() int {
	if len(m.Voltages) == 0 {
		return 0
	}
	return len(m.Voltages[0])
}
