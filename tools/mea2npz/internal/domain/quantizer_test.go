package domain

import (
	"math"
	"testing"
)

func TestQuantizeInt16_ReconstructWithinOneLSB(t *testing.T) {
	voltages := [][]float32{
		{0, 1.5, -3.2, 7.7},
		{-7.7, 0.01, 2.2, -0.5},
	}
	q := Quantize(voltages, DtypeInt16)

	if q.Dtype != DtypeInt16 {
		t.Fatalf("dtype = %s, want int16", q.Dtype)
	}
	wantScale := float64(float32(7.7)) / 32767
	if math.Abs(q.Scale-wantScale) > 1e-12 {
		t.Errorf("scale = %g, want %g", q.Scale, wantScale)
	}

	// 復元誤差が 1 LSB(=scale)未満であること
	for r, row := range voltages {
		for c, v := range row {
			recon := float32(q.Int16[r][c]) * float32(q.Scale)
			if d := math.Abs(float64(recon - v)); d > q.Scale {
				t.Errorf("[%d][%d] 復元誤差 %g > 1LSB %g", r, c, d, q.Scale)
			}
		}
	}
}

func TestQuantizeInt16_RoundHalfToEven(t *testing.T) {
	// scale=1 となるよう maxAbs=32767 を与え、.5 境界が偶数丸めされることを確認する。
	voltages := [][]float32{{32767, 0.5, 1.5, 2.5, -0.5, -1.5}}
	q := Quantize(voltages, DtypeInt16)
	if q.Scale != 1.0 {
		t.Fatalf("scale = %g, want 1.0", q.Scale)
	}
	got := q.Int16[0]
	want := []int16{32767, 0, 2, 2, 0, -2} // banker's rounding
	for i := range want {
		if got[i] != want[i] {
			t.Errorf("index %d: got %d, want %d", i, got[i], want[i])
		}
	}
}

func TestQuantizeFloat32_PassThrough(t *testing.T) {
	voltages := [][]float32{{1, 2, 3}}
	q := Quantize(voltages, DtypeFloat32)
	if q.Dtype != DtypeFloat32 || q.Scale != 1.0 {
		t.Fatalf("dtype=%s scale=%g, want float32/1.0", q.Dtype, q.Scale)
	}
	if len(q.Float32) != 1 || q.Float32[0][2] != 3 {
		t.Errorf("float32 データが保持されていない: %v", q.Float32)
	}
}

func TestQuantizeInt16_AllZero(t *testing.T) {
	q := Quantize([][]float32{{0, 0, 0}}, DtypeInt16)
	if q.Scale != 1.0 {
		t.Errorf("全ゼロ時の scale = %g, want 1.0", q.Scale)
	}
	for _, v := range q.Int16[0] {
		if v != 0 {
			t.Errorf("全ゼロ入力で非ゼロ出力: %d", v)
		}
	}
}
