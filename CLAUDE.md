# CLAUDE.md

## 言語

常に日本語で会話すること。

## プロジェクト概要

pyMEA - 多点電極アレイ(MEA)システムで取得した心筋細胞・神経細胞の細胞外電位計測データを解析するためのPythonライブラリ。計測データの読み込み、グラフ描画、数値計算を提供する。研究者がpipでインストールして利用する。

- パッケージ名: `pyMEA`
- バージョン管理: `setup.py` の `version` フィールド
- ライセンス: MIT
- 論文: [K.Kito et al (2024) Biophysics and Physicobiology, e210026](https://doi.org/10.2142/biophysico.bppb-v21.0026)

## アーキテクチャ

PyMEAクラスがファサードとして各責務クラスを保持する構成:

```
PyMEA (frozen dataclass)
  ├── data:       MEA        # 計測データ (電位データ, GAIN, サンプリングレート)
  ├── fig:        FigMEA     # グラフ描画
  ├── calculator: Calculator # 数値計算 (ISI, FPD, Conduction Velocity)
  └── electrode:  Electrode  # 電極位置情報
```

## パッケージ構成 (DDDレイヤー)

```
pyMEA/
  ├── domain/              # 外部I/O・matplotlibに依存しない
  │   ├── model/           # MEA, Electrode, FilterType, HedPath, BioPath, HedData, peak_model
  │   ├── value/           # AbstractValues, ISI, FPD, ConductionVelocity
  │   ├── service/         # peak_detection, burst, calculator, FilterMEA, CardioAveWave, peak_times, gradient/
  │   └── validators.py    # ch_validator, time_validator
  ├── application/         # PyMEAファサード, read_MEA, MutableMEA
  ├── infrastructure/      # read_bio (.hed/.bioファイルI/O)
  ├── presentation/        # FigMEA, video, FigImage, output, value_plots, gradient_plots, plot/
  ├── constants.py         # NUM_ELECTRODES, ELECTRODE_GRID_SIZE 等の定数
  └── __init__.py          # 公開API (PEP 562の遅延エクスポート)
```

**依存方向ルール**: domain → なし / infrastructure → domain / presentation → domain / application → 全層。逆方向は禁止。

- ドメイン層の描画メソッド (`ISI.show()`, `Gradient.draw2d()` 等) は presentation 層の実装へ遅延importで委譲する (domainのimport時にmatplotlibを読み込まない)
- 公開API (`pyMEA/__init__.py` の `__all__`) は利用者との契約。シグネチャ・入出力を変更しないこと。`test/src/unit/test_public_api.py` が回帰テストとして守っている

## 技術スタック

- Python 3.12
- NumPy, SciPy (信号処理・数値計算)
- Matplotlib (グラフ描画)
- pandas (データ操作)
- scikit-learn (機械学習ユーティリティ)
- imageio, Pillow (画像・動画生成)
- ビルド: setuptools (`setup.py`)
- venv: `./venv` (Python 3.9で作成、.gitignoreに未登録だが管理外)

## 設計方針

- **イミュータブル設計**: 全主要クラスが `@dataclass(frozen=True)` を使用。MEAクラスの `array` も `setflags(write=False)` で凍結
- **新インスタンス生成**: データ変換時は常に新しいインスタンスを返す (`from_slice`, `init_time`, `down_sampling` 等)
- **電極番号**: 1-64 (8x8グリッド)。`array[0]` は時間データ、`array[1]`〜`array[64]` が電極データ
- **デコレータパターン**: `@ch_validator`, `@time_validator` (入力バリデーション, `domain/validators.py`) / `@channel`, `@output_buf` (描画出力切替, `presentation/output.py`)

## テスト

```bash
# テスト実行
python -m pytest test/

# テストデータは test/resources/ に配置 (.gitignore対象)
```

- テスト構成: `test/src/unit/` (ユニットテスト), `test/src/integration/` (統合テスト)
- テストデータ取得: `test/utils.py` の `get_resource_path()` を使用

## 開発コマンド

```bash
# インストール (開発用)
pip install -e .

# パッケージインストール (ユーザー用)
pip install git+https://github.com/kkito0726/MEA_modules.git
```

## 使い方

詳細は `README_ja.md` を参照。基本フロー:

```python
from pyMEA import *

mea = read_MEA("path/to.hed", start=0, end=5, electrode_distance=450)
peak_index_neg = detect_peak_neg(mea.data)
isi = mea.calculator.isi(peak_index_neg, ch=6)
mea.fig.showAll()
```
