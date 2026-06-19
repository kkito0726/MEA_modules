package npz

import (
	"archive/zip"
	"encoding/binary"
	"io"
	"math"
	"path/filepath"
	"testing"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

func readZipMember(t *testing.T, path, name string) []byte {
	t.Helper()
	r, err := zip.OpenReader(path)
	if err != nil {
		t.Fatalf("zip open: %v", err)
	}
	defer r.Close()
	for _, f := range r.File {
		if f.Name == name {
			rc, err := f.Open()
			if err != nil {
				t.Fatalf("member open: %v", err)
			}
			defer rc.Close()
			b, _ := io.ReadAll(rc)
			return b
		}
	}
	t.Fatalf("メンバが見つからない: %s", name)
	return nil
}

func TestWriter_Int16_RoundTripAndMeta(t *testing.T) {
	voltages := [][]float32{
		{0, 1.5, -3.2, 7.7},
		{-7.7, 0.01, 2.2, -0.5},
		{1, 2, 3, 4},
	}
	m := domain.Measurement{
		Voltages:     voltages,
		SamplingRate: 10000,
		Gain:         50000,
		Start:        30,
		End:          60,
	}
	out := filepath.Join(t.TempDir(), "sub", "data.npz")
	// resetTime=true → start=0, end=30 になるはず
	w := NewWriter(out, domain.DtypeInt16, 450, true, "/path/data.hed")
	if err := w.Write(m); err != nil {
		t.Fatalf("write: %v", err)
	}

	// メタ情報
	if got := int64(binary.LittleEndian.Uint64(npyData(t, readZipMember(t, out, "sampling_rate.npy")))); got != 10000 {
		t.Errorf("sampling_rate=%d", got)
	}
	if got := int64(binary.LittleEndian.Uint64(npyData(t, readZipMember(t, out, "gain.npy")))); got != 50000 {
		t.Errorf("gain=%d", got)
	}
	if got := int64(binary.LittleEndian.Uint64(npyData(t, readZipMember(t, out, "electrode_distance.npy")))); got != 450 {
		t.Errorf("electrode_distance=%d", got)
	}
	if got := f64(npyData(t, readZipMember(t, out, "start.npy"))); got != 0 {
		t.Errorf("start=%g, want 0 (reset)", got)
	}
	if got := f64(npyData(t, readZipMember(t, out, "end.npy"))); got != 30 {
		t.Errorf("end=%g, want 30 (reset)", got)
	}

	// dtype 文字列
	dtypeBytes := npyData(t, readZipMember(t, out, "dtype.npy"))
	if got := utf32(dtypeBytes); got != "int16" {
		t.Errorf("dtype=%q", got)
	}

	// voltages 復元(scale を掛けて 1 LSB 未満)
	scale := f64(npyData(t, readZipMember(t, out, "scale.npy")))
	_, shape, vdata := parseNpy(t, readZipMember(t, out, "voltages.npy"))
	if shape != "3, 4" {
		t.Errorf("voltages shape=%q, want '3, 4'", shape)
	}
	idx := 0
	for r := 0; r < 3; r++ {
		for c := 0; c < 4; c++ {
			q := int16(binary.LittleEndian.Uint16(vdata[idx*2:]))
			idx++
			recon := float64(float32(q) * float32(scale))
			if d := math.Abs(recon - float64(voltages[r][c])); d > scale {
				t.Errorf("[%d][%d] 復元誤差 %g > 1LSB %g", r, c, d, scale)
			}
		}
	}
}

func TestWriter_KeepTime(t *testing.T) {
	m := domain.Measurement{
		Voltages: [][]float32{{1, 2}}, SamplingRate: 10000, Gain: 50000, Start: 30, End: 60,
	}
	out := filepath.Join(t.TempDir(), "k.npz")
	w := NewWriter(out, domain.DtypeFloat32, 450, false, "/p/x.hed") // keep-time
	if err := w.Write(m); err != nil {
		t.Fatalf("write: %v", err)
	}
	if got := f64(npyData(t, readZipMember(t, out, "start.npy"))); got != 30 {
		t.Errorf("start=%g, want 30 (keep-time)", got)
	}
	if got := f64(npyData(t, readZipMember(t, out, "end.npy"))); got != 60 {
		t.Errorf("end=%g, want 60 (keep-time)", got)
	}
	if got := utf32(npyData(t, readZipMember(t, out, "dtype.npy"))); got != "float32" {
		t.Errorf("dtype=%q", got)
	}
}

// --- helpers: .npy のデータ部のみ取り出す/スカラ復号 ---

func npyData(t *testing.T, b []byte) []byte {
	t.Helper()
	hlen := int(binary.LittleEndian.Uint16(b[8:10]))
	return b[10+hlen:]
}

func f64(b []byte) float64 { return math.Float64frombits(binary.LittleEndian.Uint64(b)) }

func utf32(b []byte) string {
	runes := make([]rune, 0, len(b)/4)
	for i := 0; i+4 <= len(b); i += 4 {
		runes = append(runes, rune(binary.LittleEndian.Uint32(b[i:])))
	}
	return string(runes)
}
