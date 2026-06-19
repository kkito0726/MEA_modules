package domain

import "math"

// 16bit 符号付き整数の正側最大値(pyMEA の _INT16_MAX と一致)。
const int16QuantMax = 32767

// Quantized は量子化済みの保存表現。Dtype に応じて Int16 または Float32 が有効。
// Scale は int16 復元係数(float32 時は 1.0)。
type Quantized struct {
	Dtype   Dtype
	Scale   float64
	Int16   [][]int16
	Float32 [][]float32
}

// Quantize は電位データを保存表現へ量子化する純粋関数(ドメインサービス)。
//
// int16: scale = max(|V|)/32767 で割り、偶数丸め(banker's rounding)で int16 化する。
//
//	pyMEA の save_mea_npz と同じ計算(voltages は float32、scale は max_abs/32767)。
//
// float32: そのまま保持し scale=1.0。
func Quantize(voltages [][]float32, dt Dtype) Quantized {
	if dt == DtypeFloat32 {
		return Quantized{Dtype: DtypeFloat32, Scale: 1.0, Float32: voltages}
	}

	// int16: 全要素の絶対値最大を float32 で求める(np.max(np.abs(voltages)) 相当)
	var maxAbs float32
	for _, row := range voltages {
		for _, v := range row {
			if v < 0 {
				v = -v
			}
			if v > maxAbs {
				maxAbs = v
			}
		}
	}

	scale := 1.0
	if maxAbs > 0 {
		scale = float64(maxAbs) / int16QuantMax
	}
	// numpy は float32 配列 / python float を float32 で計算する(NEP50)。
	// 同じ精度経路を再現するため float32 で割ってから偶数丸めする。
	scale32 := float32(scale)

	out := make([][]int16, len(voltages))
	for r, row := range voltages {
		o := make([]int16, len(row))
		for c, v := range row {
			ri := math.RoundToEven(float64(v / scale32))
			// numpy の .astype(int16) はオーバーフロー時に wrap(modulo)するが、
			// scale=max(|V|)/32767 ゆえ |ri| は 32767 を超えない。念のためクランプして
			// 不正値より安全側に倒す(実データでは発火しない)。
			if ri > 32767 {
				ri = 32767
			} else if ri < -32768 {
				ri = -32768
			}
			o[c] = int16(ri)
		}
		out[r] = o
	}
	return Quantized{Dtype: DtypeInt16, Scale: scale, Int16: out}
}
