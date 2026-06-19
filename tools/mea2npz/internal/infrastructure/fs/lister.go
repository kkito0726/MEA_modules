// Package fs は usecase.FileLister をローカルファイルシステムで実装する。
package fs

import (
	"io/fs"
	"os"
	"path/filepath"
	"strings"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/usecase"
)

// 一括変換の出力先ディレクトリ名。スキャン対象から除外し、再変換の混入を防ぐ。
const outputDirName = "output"

// Lister はディレクトリから .hed ファイルを列挙する。
type Lister struct{}

// コンパイル時に調停ポートの実装を強制する。
var _ usecase.FileLister = (*Lister)(nil)

// NewLister は Lister を生成する。
func NewLister() *Lister { return &Lister{} }

func isHed(name string) bool {
	return strings.HasSuffix(strings.ToLower(name), ".hed")
}

// List は root 配下の .hed を列挙する。recursive=true でサブフォルダも辿る。
// "output" ディレクトリは除外する。
func (l *Lister) List(root string, recursive bool) ([]string, error) {
	if !recursive {
		entries, err := os.ReadDir(root)
		if err != nil {
			return nil, err
		}
		var files []string
		for _, e := range entries {
			if !e.IsDir() && isHed(e.Name()) {
				files = append(files, filepath.Join(root, e.Name()))
			}
		}
		return files, nil
	}

	var files []string
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			if d.Name() == outputDirName && path != root {
				return filepath.SkipDir
			}
			return nil
		}
		if isHed(d.Name()) {
			files = append(files, path)
		}
		return nil
	})
	if err != nil {
		return nil, err
	}
	return files, nil
}
