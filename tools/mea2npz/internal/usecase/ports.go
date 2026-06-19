// Package usecase は変換フローの調停とアプリの段取り用ポートを提供する。
// データ読込/書込のポートは domain 側(リポジトリポート)に置く。
package usecase

// FileLister はディレクトリから変換対象を列挙する調停ポート。
type FileLister interface {
	List(root string, recursive bool) ([]string, error)
}

// ProgressReporter は一括変換の進捗・サマリを通知する調停ポート。
type ProgressReporter interface {
	Done(path string)                  // 変換成功
	Skipped(path string, reason error) // バリデーション等でスキップ(処理は継続)
	Failed(path string, err error)     // 実行時エラーでスキップ(処理は継続)
	Summary() (ok, skipped, failed int)
}
