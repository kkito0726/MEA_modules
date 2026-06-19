package cli

import (
	"bytes"
	"strings"
	"testing"
)

func TestPrintBanner_ContainsInfo(t *testing.T) {
	var buf bytes.Buffer
	printBanner(&buf, false)
	out := buf.String()

	if !strings.Contains(out, "███") {
		t.Errorf("ASCII アートが含まれていない")
	}
	if !strings.Contains(out, "v"+Version) {
		t.Errorf("バージョンが含まれていない")
	}
	if !strings.Contains(out, repoURL) {
		t.Errorf("リポジトリURLが含まれていない")
	}
}

func TestPrintBanner_ColorWraps(t *testing.T) {
	var buf bytes.Buffer
	printBanner(&buf, true)
	out := buf.String()
	if !strings.Contains(out, "\033[36m") || !strings.Contains(out, "\033[0m") {
		t.Errorf("color=true で ANSI 色コードが付与されていない")
	}
}

func TestPrintVersion_GNUStyle(t *testing.T) {
	var buf bytes.Buffer
	printVersion(&buf)
	out := buf.String()

	for _, want := range []string{
		"mea2npz " + Version,
		"Copyright (C) " + copyrightYear + " " + author,
		"License: " + license,
		"Written by " + author + ".",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("--version 出力に %q が含まれていない\n%s", want, out)
		}
	}
}
