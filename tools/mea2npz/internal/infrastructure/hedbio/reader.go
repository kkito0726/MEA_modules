// Package hedbio は domain.MeasurementReader を .hed/.bio 形式で実装する。
// pyMEA の decode_hed / read_bio 相当の解読・スケーリングを担う。
package hedbio

import (
	"encoding/binary"
	"fmt"
	"os"
	"strings"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

const (
	numElectrodes  = 64
	dataUnitLength = numElectrodes + 4 // 68 = 64ch + 4
	referenceGain  = 50000
	voltRange      = 100.0 // mV
)

// 電位換算係数: volt_range / (2^16 - 2) * 4 (pyMEA read_bio と一致)
var convFactor = voltRange / (1<<16 - 2) * 4

// .hed の解読テーブル(pyMEA decode_hed と一致)
var rateTable = map[int16]int{0: 100000, 1: 50000, 2: 25000, 3: 20000, 4: 10000, 5: 5000}
var gainTable = map[int16]int{
	16436: 20, 16473: 100, 16527: 1000, 16543: 2000,
	16563: 5000, 16579: 10000, 16595: 20000, 16616: 50000,
}

// Reader は単一の .hed/.bio ペアを読み込む。
type Reader struct {
	hedPath string
}

// コンパイル時にリポジトリポートの実装を強制する。
var _ domain.MeasurementReader = (*Reader)(nil)

// NewReader は .hed パスを受けて Reader を生成する。
func NewReader(hedPath string) *Reader {
	return &Reader{hedPath: hedPath}
}

func bioPathFor(hedPath string) string {
	// 拡張子(.hed)を除いたベース名 + "0001.bio"
	if i := strings.LastIndex(hedPath, "."); i >= 0 {
		hedPath = hedPath[:i]
	}
	return hedPath + "0001.bio"
}

// decodeHed は .hed からサンプリングレートと GAIN を解読する。
func (r *Reader) decodeHed() (samplingRate, gain int, err error) {
	raw, err := os.ReadFile(r.hedPath)
	if err != nil {
		return 0, 0, &domain.ValidationError{Msg: fmt.Sprintf(".hed を読み込めません: %s: %v", r.hedPath, err)}
	}
	if len(raw)/2 < 17 {
		return 0, 0, &domain.ValidationError{Msg: fmt.Sprintf(".hed が短すぎます: %s", r.hedPath)}
	}
	at := func(i int) int16 { return int16(binary.LittleEndian.Uint16(raw[i*2:])) }

	sr, ok := rateTable[at(16)]
	if !ok {
		return 0, 0, &domain.ValidationError{Msg: fmt.Sprintf("未知のサンプリングレートコード %d: %s", at(16), r.hedPath)}
	}
	g, ok := gainTable[at(3)]
	if !ok {
		return 0, 0, &domain.ValidationError{Msg: fmt.Sprintf("未知のGAINコード %d: %s", at(3), r.hedPath)}
	}
	return sr, g, nil
}

// Info は .hed/.bio ペアの計測メタ情報を返す。電位データは読まない。
func (r *Reader) Info(distance int) (domain.MeasurementInfo, error) {
	sr, gain, err := r.decodeHed()
	if err != nil {
		return domain.MeasurementInfo{}, err
	}
	bioPath := bioPathFor(r.hedPath)
	fi, err := os.Stat(bioPath)
	if err != nil {
		return domain.MeasurementInfo{}, &domain.ValidationError{
			Msg: fmt.Sprintf(".bio が見つかりません: %s", bioPath)}
	}
	nFrames := int(fi.Size()) / 2 / dataUnitLength
	return domain.MeasurementInfo{
		SamplingRate:      sr,
		Gain:              gain,
		Start:             0,
		End:               float64(nFrames) / float64(sr),
		ElectrodeDistance: distance,
		HasDistance:       distance > 0,
	}, nil
}

// Load は指定時間窓の計測データを読み込む。
func (r *Reader) Load(w domain.TimeWindow) (domain.Measurement, error) {
	sr, gain, err := r.decodeHed()
	if err != nil {
		return domain.Measurement{}, err
	}

	bioPath := bioPathFor(r.hedPath)
	fi, err := os.Stat(bioPath)
	if err != nil {
		return domain.Measurement{}, &domain.ValidationError{Msg: fmt.Sprintf(".bio が見つかりません: %s", bioPath)}
	}
	totalElems := int(fi.Size()) / 2

	startSample := w.StartSec * sr
	offsetElems := startSample * dataUnitLength
	if offsetElems > totalElems {
		return domain.Measurement{}, &domain.ValidationError{
			Msg: fmt.Sprintf("start=%ds がデータ長を超えています: %s", w.StartSec, bioPath)}
	}

	var countElems int
	if w.Full {
		countElems = totalElems - offsetElems
		countElems -= countElems % dataUnitLength // 末尾の不完全フレームを落とす
	} else {
		countElems = (w.EndSec - w.StartSec) * sr * dataUnitLength
		if offsetElems+countElems > totalElems {
			return domain.Measurement{}, &domain.ValidationError{
				Msg: fmt.Sprintf("end=%ds がデータ長を超えています: %s", w.EndSec, bioPath)}
		}
	}
	if countElems <= 0 {
		return domain.Measurement{}, &domain.ValidationError{Msg: fmt.Sprintf("読み込む区間が空です: %s", bioPath)}
	}

	f, err := os.Open(bioPath)
	if err != nil {
		return domain.Measurement{}, err
	}
	defer f.Close()

	buf := make([]byte, countElems*2)
	if _, err := f.ReadAt(buf, int64(offsetElems*2)); err != nil {
		return domain.Measurement{}, fmt.Errorf(".bio の読み込みに失敗しました: %s: %w", bioPath, err)
	}

	nFrames := countElems / dataUnitLength
	ampNeeded := gain != referenceGain
	amp := 1.0
	if ampNeeded {
		amp = float64(referenceGain) / float64(gain)
	}

	voltages := make([][]float32, numElectrodes)
	for e := range voltages {
		voltages[e] = make([]float32, nFrames)
	}
	for i := 0; i < nFrames; i++ {
		base := i * dataUnitLength
		for e := 0; e < numElectrodes; e++ {
			// 先頭4列(時刻等)を除いた電極データは列 4..67
			rawv := int16(binary.LittleEndian.Uint16(buf[(base+4+e)*2:]))
			// pyMEA read_bio の計算順を忠実に再現する(float64 の結合則は成り立たないため、
			// raw*conv を先に行い、その後で amp を別途掛ける)。
			v := float64(rawv) * convFactor
			if ampNeeded {
				v *= amp
			}
			voltages[e][i] = float32(v)
		}
	}

	start := float64(w.StartSec)
	end := start + float64(nFrames)/float64(sr)

	return domain.Measurement{
		Voltages:     voltages,
		SamplingRate: sr,
		Gain:         gain,
		Start:        start,
		End:          end,
	}, nil
}
