package npz

import (
	"archive/zip"
	"encoding/binary"
	"fmt"
	"io"
	"math"
	"strconv"
	"strings"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

// InfoReader は domain.MeasurementInfoReader の .npz 実装。
// 電位データ(voltages)は読まず、スカラのメタ情報のみを取り出す。
type InfoReader struct {
	path string
}

// NewInfoReader は .npz メタ情報リーダを生成する。
func NewInfoReader(path string) *InfoReader {
	return &InfoReader{path: path}
}

// コンパイル時にリポジトリポートの実装を強制する。
var _ domain.MeasurementInfoReader = (*InfoReader)(nil)

// Info は .npz の計測メタ情報を読み取る。
func (r *InfoReader) Info() (domain.MeasurementInfo, error) {
	zr, err := zip.OpenReader(r.path)
	if err != nil {
		return domain.MeasurementInfo{}, &domain.ValidationError{
			Msg: fmt.Sprintf(".npz を開けません: %s: %v", r.path, err)}
	}
	defer zr.Close()

	members := make(map[string][]byte, len(zr.File))
	for _, f := range zr.File {
		rc, err := f.Open()
		if err != nil {
			return domain.MeasurementInfo{}, err
		}
		b, err := io.ReadAll(rc)
		rc.Close()
		if err != nil {
			return domain.MeasurementInfo{}, err
		}
		members[f.Name] = b
	}

	sr, err := scalarInt64(members, "sampling_rate.npy")
	if err != nil {
		return domain.MeasurementInfo{}, err
	}
	gain, err := scalarInt64(members, "gain.npy")
	if err != nil {
		return domain.MeasurementInfo{}, err
	}
	start, err := scalarFloat64(members, "start.npy")
	if err != nil {
		return domain.MeasurementInfo{}, err
	}
	end, err := scalarFloat64(members, "end.npy")
	if err != nil {
		return domain.MeasurementInfo{}, err
	}

	info := domain.MeasurementInfo{
		SamplingRate: int(sr),
		Gain:         int(gain),
		Start:        start,
		End:          end,
	}
	// 電極間距離は旧形式に無いことがあるため任意扱い。
	if b, ok := members["electrode_distance.npy"]; ok {
		if d, err := parseScalarInt64(b); err == nil {
			info.ElectrodeDistance = int(d)
			info.HasDistance = true
		}
	}
	if b, ok := members["dtype.npy"]; ok {
		if s, err := parseNpyString(b); err == nil {
			info.Dtype = s
		}
	}
	return info, nil
}

func scalarInt64(members map[string][]byte, name string) (int64, error) {
	b, ok := members[name]
	if !ok {
		return 0, &domain.ValidationError{Msg: fmt.Sprintf(".npz に %s がありません(非対応の形式)", name)}
	}
	return parseScalarInt64(b)
}

func scalarFloat64(members map[string][]byte, name string) (float64, error) {
	b, ok := members[name]
	if !ok {
		return 0, &domain.ValidationError{Msg: fmt.Sprintf(".npz に %s がありません(非対応の形式)", name)}
	}
	return parseScalarFloat64(b)
}

// npyPayload は .npy(v1.0/2.0)から descr とデータ部を取り出す。
func npyPayload(b []byte) (descr string, data []byte, err error) {
	if len(b) < 10 || string(b[:6]) != "\x93NUMPY" {
		return "", nil, fmt.Errorf("npy マジックが不正")
	}
	major := b[6]
	var header string
	switch major {
	case 1:
		hlen := int(binary.LittleEndian.Uint16(b[8:10]))
		if 10+hlen > len(b) {
			return "", nil, fmt.Errorf("npy ヘッダ長が不正")
		}
		header = string(b[10 : 10+hlen])
		data = b[10+hlen:]
	default: // 2.0 以降は 4バイトヘッダ長
		if len(b) < 12 {
			return "", nil, fmt.Errorf("npy ヘッダが短すぎます")
		}
		hlen := int(binary.LittleEndian.Uint32(b[8:12]))
		if 12+hlen > len(b) {
			return "", nil, fmt.Errorf("npy ヘッダ長が不正")
		}
		header = string(b[12 : 12+hlen])
		data = b[12+hlen:]
	}
	descr = between(header, "'descr': '", "'")
	return descr, data, nil
}

func parseScalarInt64(b []byte) (int64, error) {
	descr, data, err := npyPayload(b)
	if err != nil {
		return 0, err
	}
	if descr != "<i8" {
		return 0, fmt.Errorf("int64 を期待しましたが descr=%q", descr)
	}
	if len(data) < 8 {
		return 0, fmt.Errorf("int64 データが不足")
	}
	return int64(binary.LittleEndian.Uint64(data)), nil
}

func parseScalarFloat64(b []byte) (float64, error) {
	descr, data, err := npyPayload(b)
	if err != nil {
		return 0, err
	}
	if descr != "<f8" {
		return 0, fmt.Errorf("float64 を期待しましたが descr=%q", descr)
	}
	if len(data) < 8 {
		return 0, fmt.Errorf("float64 データが不足")
	}
	return math.Float64frombits(binary.LittleEndian.Uint64(data)), nil
}

func parseNpyString(b []byte) (string, error) {
	descr, data, err := npyPayload(b)
	if err != nil {
		return "", err
	}
	if !strings.HasPrefix(descr, "<U") {
		return "", fmt.Errorf("文字列を期待しましたが descr=%q", descr)
	}
	n, err := strconv.Atoi(strings.TrimPrefix(descr, "<U"))
	if err != nil {
		return "", err
	}
	runes := make([]rune, 0, n)
	for i := 0; i < n && (i*4+4) <= len(data); i++ {
		cp := binary.LittleEndian.Uint32(data[i*4:])
		if cp == 0 {
			break // numpy は短い文字列をゼロ埋めする
		}
		runes = append(runes, rune(cp))
	}
	return string(runes), nil
}

func between(s, pre, post string) string {
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
