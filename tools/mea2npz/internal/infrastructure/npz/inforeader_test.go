package npz

import (
	"math"
	"os"
	"path/filepath"
	"testing"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

func TestInfoReader_ReadsMetadata(t *testing.T) {
	m := domain.Measurement{
		Voltages:     [][]float32{{1, 2, 3, 4}, {-1, -2, -3, -4}},
		SamplingRate: 5000,
		Gain:         50000,
		Start:        30,
		End:          60,
	}
	out := filepath.Join(t.TempDir(), "x.npz")
	// keep-time(false=reset しない)で start=30/end=60 を保存
	if err := NewWriter(out, domain.DtypeInt16, 450, false, "/p/x.hed").Write(m); err != nil {
		t.Fatalf("write: %v", err)
	}

	info, err := NewInfoReader(out).Info()
	if err != nil {
		t.Fatalf("info: %v", err)
	}
	if info.SamplingRate != 5000 {
		t.Errorf("sr=%d", info.SamplingRate)
	}
	if info.Gain != 50000 {
		t.Errorf("gain=%d", info.Gain)
	}
	if info.Start != 30 || info.End != 60 {
		t.Errorf("start/end=%g/%g", info.Start, info.End)
	}
	if math.Abs(info.DurationSec()-30) > 1e-9 {
		t.Errorf("duration=%g, want 30", info.DurationSec())
	}
	if !info.HasDistance || info.ElectrodeDistance != 450 {
		t.Errorf("distance=%d has=%v", info.ElectrodeDistance, info.HasDistance)
	}
	if info.Dtype != "int16" {
		t.Errorf("dtype=%q", info.Dtype)
	}
}

func TestInfoReader_ResetTimeDuration(t *testing.T) {
	m := domain.Measurement{
		Voltages: [][]float32{{1, 2}}, SamplingRate: 10000, Gain: 20, Start: 30, End: 60,
	}
	out := filepath.Join(t.TempDir(), "r.npz")
	// resetTime=true → start=0,end=30。duration は 30 のまま。
	if err := NewWriter(out, domain.DtypeFloat32, 300, true, "/p/r.hed").Write(m); err != nil {
		t.Fatalf("write: %v", err)
	}
	info, err := NewInfoReader(out).Info()
	if err != nil {
		t.Fatalf("info: %v", err)
	}
	if info.Start != 0 || info.End != 30 {
		t.Errorf("start/end=%g/%g, want 0/30", info.Start, info.End)
	}
	if info.DurationSec() != 30 {
		t.Errorf("duration=%g", info.DurationSec())
	}
	if info.Dtype != "float32" || info.ElectrodeDistance != 300 {
		t.Errorf("dtype=%q distance=%d", info.Dtype, info.ElectrodeDistance)
	}
}

func TestInfoReader_NotNpz(t *testing.T) {
	bad := filepath.Join(t.TempDir(), "bad.npz")
	if err := os.WriteFile(bad, []byte("not a zip"), 0o644); err != nil {
		t.Fatal(err)
	}
	_, err := NewInfoReader(bad).Info()
	if err == nil {
		t.Fatal("不正な .npz はエラーになるべき")
	}
}
