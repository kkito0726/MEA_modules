package usecase

import (
	"errors"
	"sync"

	"github.com/kkito0726/MEA_modules/tools/mea2npz/internal/domain"
)

// ConverterBuilder は入力 .hed と出力 .npz パスから ConvertUseCase を構築する。
type ConverterBuilder func(input, output string) (*ConvertUseCase, error)

// OutputResolver は入力 .hed パスから出力 .npz パスを決める。
type OutputResolver func(input string) (string, error)

// BatchConvertUseCase はディレクトリ配下の計測データを一括変換する。
// バリデーション失敗・実行時エラーともにファイル単位でスキップ(ログ)し、処理を止めない。
type BatchConvertUseCase struct {
	lister    FileLister
	reporter  ProgressReporter
	build     ConverterBuilder
	outputFor OutputResolver
	window    domain.TimeWindow
	jobs      int
}

// NewBatch は BatchConvertUseCase を生成する。
func NewBatch(
	lister FileLister,
	reporter ProgressReporter,
	build ConverterBuilder,
	outputFor OutputResolver,
	window domain.TimeWindow,
	jobs int,
) *BatchConvertUseCase {
	if jobs < 1 {
		jobs = 1
	}
	return &BatchConvertUseCase{
		lister:    lister,
		reporter:  reporter,
		build:     build,
		outputFor: outputFor,
		window:    window,
		jobs:      jobs,
	}
}

// Execute は対象を列挙し、並列に変換する。途中でプロセスを落とさず最後まで処理する。
func (b *BatchConvertUseCase) Execute(root string, recursive bool) error {
	files, err := b.lister.List(root, recursive)
	if err != nil {
		return err
	}

	sem := make(chan struct{}, b.jobs)
	var wg sync.WaitGroup
	for _, input := range files {
		wg.Add(1)
		go func(input string) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()
			b.convertOne(input)
		}(input)
	}
	wg.Wait()
	return nil
}

// convertOne は1ファイルを変換し、結果を reporter へ通知する。
// バリデーション由来のエラーは Skipped、それ以外は Failed として集約する(いずれも継続)。
func (b *BatchConvertUseCase) convertOne(input string) {
	output, err := b.outputFor(input)
	if err != nil {
		b.report(input, err)
		return
	}
	conv, err := b.build(input, output)
	if err != nil {
		b.report(input, err)
		return
	}
	if _, err := conv.Execute(b.window); err != nil {
		b.report(input, err)
		return
	}
	b.reporter.Done(input)
}

func (b *BatchConvertUseCase) report(input string, err error) {
	var ve *domain.ValidationError
	if errors.As(err, &ve) {
		b.reporter.Skipped(input, err)
	} else {
		b.reporter.Failed(input, err)
	}
}
