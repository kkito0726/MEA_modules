package cli

import "testing"

func TestUnquotePath(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"シングルクォート(Finder)", "'/Volumes/Extreme SSD/研究データ/230411'", "/Volumes/Extreme SSD/研究データ/230411"},
		{"ダブルクォート(Windows)", `"C:\Users\me\data 230411"`, `C:\Users\me\data 230411`},
		{"引用符なし", "/home/me/data.hed", "/home/me/data.hed"},
		{"前後の空白を除去", "  /home/me/data.hed  ", "/home/me/data.hed"},
		{"クォート+前後空白", "  '/home/me/data.hed'  ", "/home/me/data.hed"},
		{"両端が不一致なら外さない", `'/home/me/data.hed"`, `'/home/me/data.hed"`},
		{"片側だけのクォートは外さない", "'/home/me/data.hed", "'/home/me/data.hed"},
		{"空文字", "", ""},
		{"クォート1文字のみ", "'", "'"},
		{"空のクォート", "''", ""},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := unquotePath(c.in); got != c.want {
				t.Errorf("unquotePath(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}
