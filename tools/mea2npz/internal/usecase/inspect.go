package usecase

import "github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"

// InspectUseCase は .npz の計測メタ情報を取得する。
type InspectUseCase struct {
	reader domain.MeasurementInfoReader
}

// NewInspect は InspectUseCase を生成する。
func NewInspect(reader domain.MeasurementInfoReader) *InspectUseCase {
	return &InspectUseCase{reader: reader}
}

// Execute は計測メタ情報を返す。
func (u *InspectUseCase) Execute() (domain.MeasurementInfo, error) {
	return u.reader.Info()
}
