package npz

import (
	"archive/zip"
	"os"
	"path/filepath"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

// Writer は domain.MeasurementWriter の .npz 実装。
// 構築時にパス・dtype・電極間距離・時刻リセット可否・元 .hed パスを受け取る。
type Writer struct {
	path      string
	dtype     domain.Dtype
	distance  int
	resetTime bool
	hedPath   string
}

// コンパイル時にリポジトリポートの実装を強制する。
var _ domain.MeasurementWriter = (*Writer)(nil)

// NewWriter は .npz ライタを生成する。
func NewWriter(path string, dtype domain.Dtype, distance int, resetTime bool, hedPath string) *Writer {
	return &Writer{
		path:      path,
		dtype:     dtype,
		distance:  distance,
		resetTime: resetTime,
		hedPath:   hedPath,
	}
}

// Write は計測データを .npz(ZIP+DEFLATE)で保存する。
// pyMEA の npz_io.save_mea_npz と同じキー・dtype で書き出す(時刻行は保存しない)。
func (w *Writer) Write(m domain.Measurement) error {
	q := domain.Quantize(m.Voltages, w.dtype)

	startMeta, endMeta := m.Start, m.End
	if w.resetTime {
		startMeta = 0
		endMeta = m.End - m.Start
	}

	var voltagesNpy []byte
	if q.Dtype == domain.DtypeInt16 {
		voltagesNpy = npyInt16_2D(q.Int16)
	} else {
		voltagesNpy = npyFloat32_2D(q.Float32)
	}

	// pyMEA npz_io.py のキー順に合わせる。
	entries := []struct {
		name string
		data []byte
	}{
		{"hed_path.npy", npyString(w.hedPath)},
		{"voltages.npy", voltagesNpy},
		{"sampling_rate.npy", npyScalarInt64(int64(m.SamplingRate))},
		{"gain.npy", npyScalarInt64(int64(m.Gain))},
		{"start.npy", npyScalarFloat64(startMeta)},
		{"end.npy", npyScalarFloat64(endMeta)},
		{"dtype.npy", npyString(string(q.Dtype))},
		{"scale.npy", npyScalarFloat64(q.Scale)},
		{"electrode_distance.npy", npyScalarInt64(int64(w.distance))},
	}

	dir := filepath.Dir(w.path)
	if dir != "" {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return err
		}
	}

	// 一時ファイルに書き切ってから rename する(途中失敗で壊れた .npz を残さない)。
	tmp, err := os.CreateTemp(dir, ".mea2npz-*.tmp")
	if err != nil {
		return err
	}
	tmpPath := tmp.Name()
	// 正常完了時は rename 済みなので Remove は no-op。異常時は一時ファイルを掃除する。
	defer func() {
		tmp.Close()
		os.Remove(tmpPath)
	}()

	zw := zip.NewWriter(tmp)
	for _, e := range entries {
		fw, err := zw.CreateHeader(&zip.FileHeader{Name: e.name, Method: zip.Deflate})
		if err != nil {
			return err
		}
		if _, err := fw.Write(e.data); err != nil {
			return err
		}
	}
	if err := zw.Close(); err != nil {
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	return os.Rename(tmpPath, w.path)
}
