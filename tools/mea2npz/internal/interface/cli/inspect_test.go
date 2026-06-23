package cli

import (
	"bytes"
	"os"
	"strings"
	"testing"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

func TestPrintInfoTable_ContainsFields(t *testing.T) {
	var buf bytes.Buffer
	info := domain.MeasurementInfo{
		SamplingRate: 5000, Gain: 50000, Start: 30, End: 60,
		ElectrodeDistance: 450, HasDistance: true, Dtype: "int16",
	}
	printInfoTable(&buf, "data.npz", info, false)
	out := buf.String()

	for _, want := range []string{
		"data.npz",
		"┌", "┐", "│", "└", // Unicode 罫線
		"電極間距離 (um)", "450",
		"サンプリングレート (Hz)", "5000",
		"GAIN", "50000",
		"データ長 (s)", "30",
		"int16",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("表に %q が含まれていない\n%s", want, out)
		}
	}
}

func TestPrintInfoTable_AlignedRows(t *testing.T) {
	var buf bytes.Buffer
	printInfoTable(&buf, "x.npz", domain.MeasurementInfo{
		SamplingRate: 5000, Gain: 50000, Start: 0, End: 1, HasDistance: false,
	}, false)

	// 罫線・ヘッダ・データの各行(box-drawing で始まる行)の表示幅が揃っていること(CJK考慮)
	want := -1
	for _, line := range strings.Split(buf.String(), "\n") {
		if line == "" {
			continue
		}
		switch {
		case strings.HasPrefix(line, "┌"), strings.HasPrefix(line, "├"),
			strings.HasPrefix(line, "└"), strings.HasPrefix(line, "│"):
			if want == -1 {
				want = dispWidth(line)
			} else if w := dispWidth(line); w != want {
				t.Errorf("行の表示幅が不一致: %d != %d\n%q", w, want, line)
			}
		}
	}
	if want == -1 {
		t.Fatal("テーブル行が見つからない")
	}
}

func TestRenderTable_ColorBoldsHeader(t *testing.T) {
	var buf bytes.Buffer
	renderTable(&buf, [2]string{"項目", "値"}, [][2]string{{"a", "b"}}, true)
	if !strings.Contains(buf.String(), "\033[1m") {
		t.Errorf("color=true でヘッダが太字化されていない")
	}
}

func TestDispWidth(t *testing.T) {
	if dispWidth("GAIN") != 4 {
		t.Errorf("ASCII 幅が不正")
	}
	if dispWidth("計測") != 4 { // 全角2文字
		t.Errorf("全角幅が不正: %d", dispWidth("計測"))
	}
	if dispWidth("計測 (s)") != 4+4 { // 全角2 + " (s)"=4
		t.Errorf("混在幅が不正: %d", dispWidth("計測 (s)"))
	}
}

func TestCollectOptions_NpzShortCircuits(t *testing.T) {
	dir := t.TempDir()
	npzPath := dir + "/data.npz"
	if err := os.WriteFile(npzPath, []byte("dummy"), 0o644); err != nil {
		t.Fatal(err)
	}
	// 入力に .npz を与えたら、変換用の追加質問なしで即 options(input のみ)を返す
	o, code, ok := collectOptions(strings.NewReader(npzPath+"\n"), &bytes.Buffer{})
	if !ok || code != 0 {
		t.Fatalf("ok=%v code=%d", ok, code)
	}
	if o.input != npzPath {
		t.Errorf("input=%q", o.input)
	}
}
