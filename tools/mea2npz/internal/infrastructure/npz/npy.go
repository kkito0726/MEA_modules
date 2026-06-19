// Package npz は domain.MeasurementWriter を .npy/.npz(ZIP+DEFLATE)で実装する。
// NumPy フォーマットの詳細(ヘッダ・dtype・UTF-32LE・64バイト境界)を隔離する。
package npz

import (
	"encoding/binary"
	"fmt"
	"math"
)

// buildNpy は .npy 形式(v1.0)のバイト列を組み立てる。
// shape は "()"(スカラ) や "64, 100"(2次元) のように括弧内の文字列を渡す。
func buildNpy(descr, shape string, raw []byte) []byte {
	header := fmt.Sprintf("{'descr': '%s', 'fortran_order': False, 'shape': (%s), }", descr, shape)

	// マジック(6) + バージョン(2) + ヘッダ長(2) + ヘッダ + 改行 を 64 バイト境界へ。
	const prefix = 10
	unpadded := prefix + len(header) + 1 // +1: 末尾の改行
	pad := (64 - unpadded%64) % 64
	for i := 0; i < pad; i++ {
		header += " "
	}
	header += "\n"

	buf := make([]byte, 0, prefix+len(header)+len(raw))
	buf = append(buf, 0x93, 'N', 'U', 'M', 'P', 'Y', 0x01, 0x00)
	var hlen [2]byte
	binary.LittleEndian.PutUint16(hlen[:], uint16(len(header)))
	buf = append(buf, hlen[:]...)
	buf = append(buf, header...)
	buf = append(buf, raw...)
	return buf
}

// npyInt16_2D は (rows × cols) の int16 配列を C順(行優先)で .npy 化する。
func npyInt16_2D(data [][]int16) []byte {
	rows := len(data)
	cols := 0
	if rows > 0 {
		cols = len(data[0])
	}
	raw := make([]byte, rows*cols*2)
	off := 0
	for _, row := range data {
		for _, v := range row {
			binary.LittleEndian.PutUint16(raw[off:], uint16(v))
			off += 2
		}
	}
	return buildNpy("<i2", fmt.Sprintf("%d, %d", rows, cols), raw)
}

// npyFloat32_2D は (rows × cols) の float32 配列を C順で .npy 化する。
func npyFloat32_2D(data [][]float32) []byte {
	rows := len(data)
	cols := 0
	if rows > 0 {
		cols = len(data[0])
	}
	raw := make([]byte, rows*cols*4)
	off := 0
	for _, row := range data {
		for _, v := range row {
			binary.LittleEndian.PutUint32(raw[off:], math.Float32bits(v))
			off += 4
		}
	}
	return buildNpy("<f4", fmt.Sprintf("%d, %d", rows, cols), raw)
}

// npyScalarInt64 は 0次元 int64 を .npy 化する。
func npyScalarInt64(v int64) []byte {
	raw := make([]byte, 8)
	binary.LittleEndian.PutUint64(raw, uint64(v))
	return buildNpy("<i8", "", raw)
}

// npyScalarFloat64 は 0次元 float64 を .npy 化する。
func npyScalarFloat64(v float64) []byte {
	raw := make([]byte, 8)
	binary.LittleEndian.PutUint64(raw, math.Float64bits(v))
	return buildNpy("<f8", "", raw)
}

// npyString は python str(0次元 <U 配列)を .npy 化する。UTF-32LE で各コードポイントを格納する。
func npyString(s string) []byte {
	runes := []rune(s)
	n := len(runes)
	if n == 0 {
		n = 1 // numpy は空文字でも <U1 を割り当てる
	}
	raw := make([]byte, n*4)
	for i, r := range runes {
		binary.LittleEndian.PutUint32(raw[i*4:], uint32(r))
	}
	return buildNpy(fmt.Sprintf("<U%d", n), "", raw)
}
