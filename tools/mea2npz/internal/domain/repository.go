package domain

// MeasurementReader は計測データの取得元を表すリポジトリポート。
// .hed/.bio 等の具体フォーマットは知らない(infrastructure が実装する)。
type MeasurementReader interface {
	// Load は指定した時間窓の計測データを読み込む。
	Load(window TimeWindow) (Measurement, error)
}

// MeasurementWriter は計測データの保存先を表すリポジトリポート。
// .npz 等の具体フォーマットは知らない(infrastructure が実装する)。
// パス・dtype・電極間距離・時刻リセット等のポリシーは実装の構築時に注入する。
type MeasurementWriter interface {
	// Write は計測データを保存する。
	Write(m Measurement) error
}
