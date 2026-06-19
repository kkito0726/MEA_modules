package hedbio

import (
	"encoding/binary"
	"math"
	"os"
	"path/filepath"
	"testing"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

// writeInt16LE は int16 スライスをLEバイト列として書き出す。
func writeInt16LE(t *testing.T, path string, vals []int16) {
	t.Helper()
	buf := make([]byte, len(vals)*2)
	for i, v := range vals {
		binary.LittleEndian.PutUint16(buf[i*2:], uint16(v))
	}
	if err := os.WriteFile(path, buf, 0o644); err != nil {
		t.Fatalf("write %s: %v", path, err)
	}
}

// makeHed は rate コード4(10000Hz)/gain コード16616(50000=参照)の .hed を作る。
func makeHed(t *testing.T, dir string) string {
	t.Helper()
	hed := make([]int16, 17)
	hed[3] = 16616 // gain=50000 → amp=1
	hed[16] = 4    // rate=10000
	path := filepath.Join(dir, "data.hed")
	writeInt16LE(t, path, hed)
	return path
}

func TestReader_Load_Full(t *testing.T) {
	dir := t.TempDir()
	hedPath := makeHed(t, dir)

	// .bio: 5フレーム × 68列。電極列(4..67)に既知値を入れる。
	const frames = 5
	raw := make([]int16, frames*dataUnitLength)
	for i := 0; i < frames; i++ {
		base := i * dataUnitLength
		for col := 0; col < dataUnitLength; col++ {
			raw[base+col] = int16(100*i + col) // 任意のパターン
		}
	}
	writeInt16LE(t, filepath.Join(dir, "data0001.bio"), raw)

	r := NewReader(hedPath)
	m, err := r.Load(domain.TimeWindow{Full: true})
	if err != nil {
		t.Fatalf("load: %v", err)
	}
	if m.SamplingRate != 10000 || m.Gain != 50000 {
		t.Fatalf("sr=%d gain=%d", m.SamplingRate, m.Gain)
	}
	if m.Channels() != 64 || m.Samples() != frames {
		t.Fatalf("channels=%d samples=%d", m.Channels(), m.Samples())
	}

	factor := 100.0 / 65534.0 * 4.0
	for e := 0; e < 64; e++ {
		for i := 0; i < frames; i++ {
			rawv := int16(100*i + (4 + e))
			want := float32(float64(rawv) * factor)
			if m.Voltages[e][i] != want {
				t.Fatalf("voltages[%d][%d]=%g want %g", e, i, m.Voltages[e][i], want)
			}
		}
	}

	// start=0, end = frames/sr
	if m.Start != 0 {
		t.Errorf("start=%g", m.Start)
	}
	if wantEnd := float64(frames) / 10000.0; math.Abs(m.End-wantEnd) > 1e-12 {
		t.Errorf("end=%g want %g", m.End, wantEnd)
	}
}

func TestReader_MissingBio_Validation(t *testing.T) {
	dir := t.TempDir()
	hedPath := makeHed(t, dir) // .bio を作らない

	r := NewReader(hedPath)
	_, err := r.Load(domain.TimeWindow{Full: true})
	if err == nil {
		t.Fatal(".bio 欠如でエラーになるべき")
	}
	var ve *domain.ValidationError
	if !errorsAs(err, &ve) {
		t.Errorf("ValidationError であるべき: %T", err)
	}
}

func TestReader_RangeOverflow_Validation(t *testing.T) {
	dir := t.TempDir()
	hedPath := makeHed(t, dir)
	// 1フレームだけ → end=1s(=10000frames)は超過
	writeInt16LE(t, filepath.Join(dir, "data0001.bio"), make([]int16, dataUnitLength))

	r := NewReader(hedPath)
	_, err := r.Load(domain.TimeWindow{StartSec: 0, EndSec: 1})
	var ve *domain.ValidationError
	if err == nil || !errorsAs(err, &ve) {
		t.Errorf("区間超過は ValidationError であるべき: %v", err)
	}
}

// errorsAs は errors.As の薄いラッパ(テスト依存を局所化)。
func errorsAs(err error, target **domain.ValidationError) bool {
	for err != nil {
		if ve, ok := err.(*domain.ValidationError); ok {
			*target = ve
			return true
		}
		type unwrapper interface{ Unwrap() error }
		u, ok := err.(unwrapper)
		if !ok {
			return false
		}
		err = u.Unwrap()
	}
	return false
}
