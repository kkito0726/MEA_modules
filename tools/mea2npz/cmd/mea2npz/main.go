// Command mea2npz は .hed/.bio を .npz へ変換する単一バイナリ CLI。
// Composition Root: 依存を配線して CLI を起動する。
package main

import (
	"os"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/interface/cli"
)

func main() {
	os.Exit(cli.Run(os.Args[1:]))
}
