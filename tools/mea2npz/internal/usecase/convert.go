package usecase

import "github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"

// ConvertUseCase は単一ファイルの変換を調停する。
// domain のリポジトリポートのみに依存し、具体フォーマット(.hed/.npz)を知らない。
type ConvertUseCase struct {
	reader domain.MeasurementReader
	writer domain.MeasurementWriter
}

// NewConvert は ConvertUseCase を生成する。
func NewConvert(reader domain.MeasurementReader, writer domain.MeasurementWriter) *ConvertUseCase {
	return &ConvertUseCase{reader: reader, writer: writer}
}

// Execute は時間窓を読み込み、保存する。保存した計測データを返す(表示・検証用)。
func (c *ConvertUseCase) Execute(window domain.TimeWindow) (domain.Measurement, error) {
	m, err := c.reader.Load(window)
	if err != nil {
		return domain.Measurement{}, err
	}
	if err := c.writer.Write(m); err != nil {
		return domain.Measurement{}, err
	}
	return m, nil
}
