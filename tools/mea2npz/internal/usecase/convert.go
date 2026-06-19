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

// Execute は時間窓を読み込み、保存する。
func (c *ConvertUseCase) Execute(window domain.TimeWindow) error {
	m, err := c.reader.Load(window)
	if err != nil {
		return err
	}
	return c.writer.Write(m)
}
