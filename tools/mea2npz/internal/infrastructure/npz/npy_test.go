package npz

import (
	"bytes"
	"encoding/binary"
	"math"
	"strings"
	"testing"
)

// parseNpy は .npy バイト列から descr/shape/データ部を取り出す簡易パーサ(テスト用)。
func parseNpy(t *testing.T, b []byte) (descr, shape string, data []byte) {
	t.Helper()
	if len(b) < 10 || !bytes.Equal(b[:6], []byte("\x93NUMPY")) {
		t.Fatalf("マジックが不正")
	}
	if b[6] != 1 || b[7] != 0 {
		t.Fatalf("バージョンが 1.0 でない: %d.%d", b[6], b[7])
	}
	hlen := int(binary.LittleEndian.Uint16(b[8:10]))
	total := 10 + hlen
	if total%64 != 0 {
		t.Fatalf("ヘッダが64バイト境界でない: total=%d", total)
	}
	header := string(b[10:total])
	descr = extract(header, "'descr': '", "'")
	shape = extract(header, "'shape': (", ")")
	return descr, shape, b[total:]
}

func extract(s, pre, post string) string {
	i := strings.Index(s, pre)
	if i < 0 {
		return ""
	}
	s = s[i+len(pre):]
	j := strings.Index(s, post)
	if j < 0 {
		return ""
	}
	return s[:j]
}

func TestBuildNpy_Alignment(t *testing.T) {
	cases := [][]byte{
		npyScalarInt64(42),
		npyScalarFloat64(3.14),
		npyString("int16"),
		npyInt16_2D([][]int16{{1, 2, 3}, {4, 5, 6}}),
		npyFloat32_2D([][]float32{{1.5, 2.5}}),
	}
	for i, b := range cases {
		hlen := int(binary.LittleEndian.Uint16(b[8:10]))
		if (10+hlen)%64 != 0 {
			t.Errorf("case %d: 64バイト境界でない", i)
		}
	}
}

func TestNpyScalars(t *testing.T) {
	descr, shape, data := parseNpy(t, npyScalarInt64(12345))
	if descr != "<i8" || shape != "" {
		t.Errorf("int64: descr=%q shape=%q", descr, shape)
	}
	if int64(binary.LittleEndian.Uint64(data)) != 12345 {
		t.Errorf("int64 値が不一致")
	}

	descr, _, data = parseNpy(t, npyScalarFloat64(2.5))
	if descr != "<f8" {
		t.Errorf("float64: descr=%q", descr)
	}
	if math.Float64frombits(binary.LittleEndian.Uint64(data)) != 2.5 {
		t.Errorf("float64 値が不一致")
	}
}

func TestNpyString_UTF32LE(t *testing.T) {
	descr, shape, data := parseNpy(t, npyString("int16"))
	if descr != "<U5" || shape != "" {
		t.Errorf("descr=%q shape=%q, want <U5/scalar", descr, shape)
	}
	if len(data) != 5*4 {
		t.Fatalf("UTF-32LE 長が不正: %d", len(data))
	}
	// 先頭コードポイント 'i' = 0x69
	if binary.LittleEndian.Uint32(data[:4]) != uint32('i') {
		t.Errorf("先頭コードポイントが 'i' でない")
	}
}

func TestNpyInt16_2D_Shape(t *testing.T) {
	_, shape, data := parseNpy(t, npyInt16_2D([][]int16{{1, 2, 3}, {4, 5, 6}}))
	if shape != "2, 3" {
		t.Errorf("shape=%q, want '2, 3'", shape)
	}
	if len(data) != 2*3*2 {
		t.Errorf("データ長が不正: %d", len(data))
	}
	// C順(行優先): 先頭は data[0][0]=1
	if int16(binary.LittleEndian.Uint16(data[:2])) != 1 {
		t.Errorf("先頭要素が 1 でない")
	}
}
