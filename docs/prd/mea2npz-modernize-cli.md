# PRD: mea2npz モダン CLI 化（対話フォーム・プログレスバー）

| 項目 | 内容 |
|---|---|
| ステータス | Draft |
| 作成日 | 2026-07-05 |
| 対象 | mea2npz（`tools/mea2npz/`・Go 単一バイナリ CLI） |
| 関連 | [`mea2npz-cli.md`](./mea2npz-cli.md)（初版 PRD） / `internal/interface/cli/`（対話・進捗・装飾） |
| 種別 | UX 改善（機能追加・非破壊） |

---

## 1. 背景・課題

mea2npz は「Python 非依存で `.hed`/`.bio` を `.npz` に変換する」目的をすでに満たしている。一方で **CLI としての操作体験（UX）は素朴なまま**で、計測現場の非エンジニア利用者にとって次の摩擦が残っている。

現状の実装（`internal/interface/cli/`）を精査した結果、以下のギャップを確認した。

| # | 現状 | 課題 |
|---|---|---|
| C1 | 対話モードは手書きの `bufio` プロンプトを縦に並べるだけ（`interactive.go`） | 見た目が地味で、どこを入力中か分かりにくい |
| C2 | **入力パスを間違えると即終了**する。`collectOptions` は `os.Stat` 失敗で `return 2`（`interactive.go:37-40`） | 打ち直しができず、最初からやり直しになる。初心者が最も詰まる箇所 |
| C3 | dtype 誤入力（`int16`/`float32` 以外）も即終了（`interactive.go:47-50`） | 選択肢を「選ぶ」形にすればそもそも誤入力が起きない |
| C4 | 進捗表示は**完了ファイルごとの `[n/総数]` カウンタのみ**（`reporter.go`）。真のプログレスバーではない | 一括変換で「あと何割か」「今どのファイルか」が視覚的に分からない |
| C5 | **単一変換は「変換開始→変換完了」の2行だけ**（`cli.go:148-165`）。大きい `.hed` の読込・保存中は無反応 | 数十秒フリーズしているように見え、固まったのか不安になる |
| C6 | y/N・整数・パスをすべて手書きプロンプトで実装（4種類のヘルパ） | 保守対象が多く、装飾も限定的 |

**課題を一言でいうと**: 変換ロジックは完成しているが、「非エンジニアが迷わず・安心して使える対話体験」に達していない。特に **パス誤入力時の再入力（C2）** と **進捗の可視化（C4/C5）** が優先度が高い。

## 2. ゴール / 非ゴール

### ゴール

- **G1** 対話モードで、誤ったパス・dtype を入力しても**その場で再入力を促す**（プロセスを落とさない）。
- **G2** 一括変換に**リアルタイムのプログレスバー**（全体進捗 + 処理中ファイル名）を出す。
- **G3** 単一変換で、読込・保存中に**動きのあるインジケータ**（スピナー/バー）を出し、無反応に見せない。
- **G4** 対話フォームを `huh` ベースの**モダンな UI**（フォーカス移動・選択肢・インライン検証）に刷新する。
- **G5** 既存のフラグ経路・出力・数値互換・テスト容易性を**一切壊さない**（非破壊）。

### 非ゴール

- 変換アルゴリズム・`.npz` フォーマット・数値互換の変更（初版 PRD の契約を維持）。
- サブコマンド体系への移行（`mea2npz convert ...` 等）。現行の「引数で自動振り分け」を維持する。
- フラグ名・既定値の変更（README にドキュメント化済み＝スクリプトからの利用契約）。
- TUI での結果ビューア・ファイルブラウザ常駐など、変換の範囲を超える機能。

## 3. 現状アーキテクチャの整理（改修範囲の特定）

すべての改修は **`internal/interface/cli/` 層に閉じる**。DDD の依存方向（`domain ← usecase ← interface`）より、対話・進捗・装飾ライブラリを domain/usecase に持ち込まない。

| 改修に関係する既存要素 | 役割 | 改修方針 |
|---|---|---|
| `interactive.go` の `collectOptions` / `prompt*` | 手書き対話 | **温存**（後述の非 TTY フォールバック兼テスト経路）。新たに huh 経路を追加 |
| `reporter.go` `consoleReporter`（`usecase.ProgressReporter` 実装） | 一括進捗のカウンタ表示 | プログレスバー実装に差し替え可能。**ポートは変更不要**（実装の入れ替えで済む） |
| `usecase.ProgressReporter`（`ports.go`） | 進捗の調停ポート | 既存の `Begin/Done/Skipped/Failed/Summary` で**一括のバーは実現可能** |
| `usecase.ConvertUseCase` / `domain.MeasurementReader`・`Writer` | 単一変換（Load→Write の2段） | 単一の**確定的**バーには進捗コールバックの追加が必要（4.3・6章で詳述） |
| `style.go` / `banner.go` | ANSI 装飾・TTY 判定・NO_COLOR | huh/lipgloss と役割が重なるが、**非 TTY プレーン出力の判定として引き続き使用** |

**重要な制約**: 一括進捗は既存ポートで差し替えできるが、単一変換の「確定的バー」は Load/Write が現在アトミックなため、進捗を刻むには reader/writer ポートへコールバックを通す必要がある。難易度が段違いなので機能を分離する（4.3）。

## 4. 改善提案

### F1. huh による対話フォーム（G1・G3・G4）

引数なし起動時の対話を [`charmbracelet/huh`](https://github.com/charmbracelet/huh) のフォームへ刷新する。

- **入力パス**: `huh.NewInput()` + `Validate` 関数。`os.Stat` で存在確認し、失敗時はフォーム内に赤字でエラーを出して**再入力を要求**（フォームが先へ進まない）。→ **C2 解消**。
  - 発展案: `huh.NewFilePicker()` を使えば、そもそもキー入力せずディレクトリを辿って選べる。パスのコピペ運用（`unquotePath`）も併存させる。
- **dtype**: `huh.NewSelect[string]()` で `int16` / `float32` を選択肢化。→ **C3 解消**（誤入力が起きない）。
- **読込区間の指定有無 / 時刻リセット / 再帰探索**: `huh.NewConfirm()`。
- **開始秒・終了秒**: `Confirm` が Yes のときだけ表示する条件付きフィールド。数値 `Validate` で非数を弾く。
- **電極間距離・出力先**: `Input`（既定値プレースホルダ）。
- 全項目を1つの `huh.Form`（複数 `huh.Group`）にまとめ、フォーカス移動・戻り・インラインエラーを提供。既定テーマを lipgloss でブランド色に寄せる。
- 最後に**確認サマリ**（入力/出力/dtype/区間）を出し、`Confirm` で実行 or やり直しを選べるようにする。

### F2. 一括変換のプログレスバー（G2）

`consoleReporter`（`usecase.ProgressReporter` 実装）を **Charm ベースのプログレス表示**へ差し替える。ポート契約は変えない。

- 全体バー: `処理済み / 総数`（`Begin(total)` で総数確定 → `Done/Skipped/Failed` ごとに前進）。`bubbles/progress` を `bubbletea` プログラムで駆動。
- 現在処理中ファイル名・成功/スキップ/失敗の内訳をバー近傍に表示。
- 並列ジョブ（`batch.go` の goroutine 群）からの通知は、`reporter` が受けて **bubbletea プログラムへ `p.Send(msg)`** で流す（描画スレッドは1本に集約し、競合を避ける）。既存の `mu sync.Mutex` によるカウント集約はそのまま活かす。
- 完了後は現行同様の `printSummary`（成功/スキップ/失敗/所要/出力先）を残す。

### F3. 単一変換の動きのあるインジケータ（G3・C5）

大きい `.hed` の読込・保存中に無反応にしない。実装コストで2段階に分ける。

- **F3a（低リスク・確定不要）**: 変換中に `bubbles/spinner`（不確定インジケータ）＋「読込中… / 保存中…」ラベルを表示。**ポート変更不要**。まずこれを入れる。
- **F3b（発展・確定バー）**: `MeasurementReader.Load` / `MeasurementWriter.Write` に**任意の進捗コールバック**（例: `func(done, total int)`）を追加し、`.bio` の読込バイト量・`.npy` 書込量で確定的バーを出す。ポート拡張を伴うため F3a と切り離し、後続フェーズで検討。

### F4. 装飾・エラー表現の統一（付随）

- `style.go` の ANSI ヘルパと重複する装飾を lipgloss に寄せ、サマリ枠・エラー枠・ヒント（`messages.go` の `hintFor`）を統一トーンに。
- `hintFor` の初心者向けヒントは維持（huh の `Validate` エラー文にも流用可能）。

## 5. 技術方針

### 5.1 採用ライブラリ（Charm エコシステム・すべて純 Go）

| ライブラリ | 用途 | 層 |
|---|---|---|
| `charmbracelet/huh` | 対話フォーム（Input/Select/Confirm/FilePicker/Validate） | interface/cli |
| `charmbracelet/bubbles`（progress, spinner） | 進捗バー・スピナー | interface/cli |
| `charmbracelet/bubbletea` | 進捗描画の実行ループ | interface/cli |
| `charmbracelet/lipgloss` | 装飾（既存 ANSI の置換/併存） | interface/cli |

いずれも CGO 不要で、現行のクロスビルド（`CGO_ENABLED=0`、Windows/macOS/Linux）を維持できる。

### 5.2 TTY フォールバックとテスト容易性（最重要）

huh/bubbletea は **TTY を要求**し、`strings.NewReader` では駆動できない。現行テスト（`interactive_test.go` は `collectOptions(strings.NewReader(...), buf)` で検証）を壊さないため、対話経路を分岐する。

```
Run(引数なし):
  TTY か? (既存 isTerminal を流用)
    ├─ Yes → huh フォーム経路（新規）
    └─ No  → 既存 collectOptions（手書きプロンプト）にフォールバック
```

- `collectOptions` と `prompt*` は**削除せず温存**する（非 TTY・CI・パイプ入力の経路 兼 単体テスト対象）。
- huh 経路は、フォーム結果を最終的に既存の `options` 構造体へ詰めて `dispatch(o)` に渡す。**振り分けロジック（`dispatch`）は共通**なので回帰リスクを閉じ込められる。
- 一括プログレスバーも、非 TTY・`NO_COLOR` 時は現行のカウンタ/行出力にフォールバックする（`colorEnabled` / `isTerminal` を条件に）。

### 5.3 互換性（G5）

- フラグ経路（`mea2npz [options] <input>`）は**完全に現状維持**。huh は「引数なし + TTY」のときだけ発動。
- `-version`、バナー、`.npz` 情報表示、一括サマリ、終了コード（成功=0 / スキップ・失敗あり=1 / 使い方エラー=2）を維持。
- 出力 `.npz` の数値互換（初版 PRD の契約）に一切触れない。

## 6. アーキテクチャ影響と変更ファイル

| ファイル | 変更 |
|---|---|
| `go.mod` / `go.sum` | Charm 依存を追加（現状 **依存ゼロ**からの変化。6.1 参照） |
| `internal/interface/cli/form.go`（新規） | huh フォーム経路。結果を `options` に詰めて返す |
| `internal/interface/cli/cli.go` | `Run` の引数なし分岐で TTY 判定 → form 経路 or `collectOptions` |
| `internal/interface/cli/progress.go`（新規） | bubbletea プログレスバー版 reporter（`usecase.ProgressReporter` 実装） |
| `internal/interface/cli/reporter.go` | 現行カウンタ版はフォールバックとして残す |
| `internal/interface/cli/interactive.go` | **変更最小**（温存）。TTY 時は呼ばれないだけ |
| `usecase.ProgressReporter`（`ports.go`） | **F2 では変更不要**。F3b を実装する場合のみ reader/writer ポートへ進捗コールバックを追加 |

### 6.1 トレードオフ: 依存ゼロ・軽量バイナリからの脱却（実測済み）

現行は **require ゼロ**の単一バイナリ。Charm 一式（huh / bubbletea / bubbles / lipgloss、間接依存は `golang.org/x/sys` のみ）を追加した場合のサイズを、実際にビルドして計測した（darwin/arm64・`CGO_ENABLED=0 -trimpath`）。

| ビルド | strip (`-s -w`) | 非 strip |
|---|---|---|
| 現行 mea2npz | 約 2.1MB | 約 3.2MB（コミット済みバイナリは 3.3MB） |
| Charm 増分（最小 import 実測） | +約 1.6MB | +約 2.2MB |
| **Charm 導入後（見込み）** | **約 3.7〜3.8MB** | **約 5.4MB** |

- **結論: 増分は strip 版で +約 1.6MB。倍増には届かず、`-ldflags="-s -w"` で配布すれば ~3.8MB に収まる。**（当初 PRD の「6〜9MB」見積もりは過大だった。）
- 純 Go のまま・CGO 不要・静的単一バイナリ・現行のクロスビルドはすべて維持。
- 副次影響: `go.sum` 管理と依存の脆弱性追従（Charm + `x/sys`）が新たに発生。
- **推奨: 外部ライブラリ導入を可とする。** 配布時は `-ldflags="-s -w"` を付与しサイズを抑える。「軽量さ」を最優先する場合のみ A2（自前バー）を選択。

## 7. リスクと対策

| リスク | 対策 |
|---|---|
| huh 導入でテスト容易性が落ちる | `collectOptions` を温存し非 TTY 経路として単体テスト継続。huh フォームは薄い配線に留め、`options` 生成後の共通経路（`dispatch`）でカバー |
| 並列 goroutine と bubbletea 描画の競合 | 描画は bubbletea 1本に集約し、reporter は `p.Send` でメッセージを送るだけにする |
| 非 TTY/CI/パイプでフォームが壊れる | TTY 判定でフォールバック。CI・パイプ・`NO_COLOR` は必ず旧経路 |
| 依存追加によるバイナリ肥大・供給網リスク | 6.1 の通り許容。重視時は A2（自前バー）を選択 |
| Windows(git bash) の端末互換 | bubbletea は Windows 対応だが、`install.sh` 経由の git bash で要動作確認（受け入れ基準に含める） |

## 8. 代替案

- **A1: huh は使わず、再入力ループだけ追加**（既存プロンプトに `os.Stat` の再試行ループを足す）。C2 は最小コストで解消できるが、C4/C5 の進捗と見た目は変わらない。**最小実装として F1 の一部を先行**する価値はある。
- **A2: 進捗バーを依存なしで自前実装**（`\r` によるインプレース更新）。依存ゼロ・軽量を維持できるが、実装・保守コストと表現力で Charm に劣る。
- **A3: フルスクリーン TUI（bubbletea 常駐）へ全面移行**。過剰。非ゴール。

推奨は **F1（huh）+ F2（一括バー）+ F3a（単一スピナー）** を本命とし、依存追加を避けたい場合のみ A1+A2 に切り替える。

## 9. 段階的実装計画

1. **Phase 0: 準備** — Go/Charm 依存追加、TTY 分岐の骨格（`Run` に form/旧経路のスイッチ）。既存テストが緑のまま通ることを確認。
2. **Phase 1: パス再入力（G1・C2）** — 最優先。huh Input + `Validate`（または A1 の再入力ループ）。dtype を Select 化（C3）。
3. **Phase 2: 対話フォーム全体（G4）** — 区間・距離・出力・再帰を huh 化。確認サマリ画面。非 TTY フォールバック確認。
4. **Phase 3: 一括プログレスバー（G2・F2）** — reporter を bubbletea 版に差し替え。並列通知を `p.Send` へ。フォールバック維持。
5. **Phase 4: 単一スピナー（G3・F3a）** — 読込/保存中のスピナー。
6. **Phase 5（発展）: 確定バー（F3b）** — reader/writer ポートに進捗コールバック。要否は Phase 4 の体験を見て判断。
7. 各フェーズで README・[`mea2npz-cli.md`](./mea2npz-cli.md) を更新し、Windows(git bash)/macOS/Linux で動作確認。

## 10. 受け入れ基準

- [ ] 対話モードで存在しないパスを入れても終了せず、再入力を求められる。
- [ ] dtype は選択式で、`int16`/`float32` 以外を選べない。
- [ ] 一括変換でプログレスバーが進捗（処理済み/総数・現在ファイル）を表示する。
- [ ] 単一変換で読込・保存中にスピナー/インジケータが動く。
- [ ] `NO_COLOR`・パイプ・CI（非 TTY）では旧来のプレーン出力にフォールバックする。
- [ ] フラグ経路・`-version`・`.npz` 情報表示・終了コード・数値互換が現状と一致（既存テスト緑）。
- [ ] Windows(git bash)/macOS/Linux で対話・進捗が破綻しない。

## 11. 未決事項（推奨対応で確定）

- ~~**Q1** 単一変換の確定バー（F3b）まで踏み込むか、スピナー（F3a）で十分か。~~ → **推奨: F3a（スピナー）を採用し、確定バー（F3b）は保留。**
  - 根拠: F3b は `MeasurementReader.Load` / `MeasurementWriter.Write` へ進捗コールバックを通す必要があり、最もきれいに保たれている **domain 層のポート契約を変更**することになる（非破壊・依存方向の方針に反しやすい）。単一変換は通常1ファイルで、利用者の不安は「固まった?」であって「あと何%か」ではないため、「読込中… / 保存中…」の2フェーズスピナーで解消できる。「あと何割」の情報価値が高い一括変換は F2 の確定バーがカバーする。**大きい .hed 1本が不透明という声が出て初めて F3b を検討する。**
- ~~**Q2** 依存追加（Charm 一式・数 MB 増）を許容するか、依存ゼロ（A2 自前バー）を維持するか。~~ → **決定: 外部ライブラリ導入を可とする（strip 版 +約 1.6MB / 合計 ~3.8MB。6.1 参照）。配布は `-ldflags="-s -w"`。**
- ~~**Q3** パス入力を `huh.FilePicker`（ブラウズ選択）にするか、テキスト入力 + `Validate`（コピペ運用維持）にするか、両対応にするか。~~ → **推奨: テキスト入力（`huh.NewInput()` + `Validate`）を主軸とし、`huh.FilePicker` は将来拡張として保留。**
  - 根拠: 当初要望「huh で誤ったパスは再入力を求める」を Input + `Validate` が直球で満たす。既存の**ドラッグ&ドロップ／コピペ運用**（`unquotePath` による引用符除去）は FilePicker では活かせず潰れてしまう。Windows(git bash) では FilePicker のドライブ跨ぎ探索が扱いにくく確認コストも増える。**対策**: 入力プロンプトのタイトルに「（ドラッグ&ドロップでも可）」と添える。FilePicker は「パスが分からない人向けの選択肢」として要望が出てから追加する。
