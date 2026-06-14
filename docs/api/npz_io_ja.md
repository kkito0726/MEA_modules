# .npz 保存・読み込み

MEA計測データを圧縮した `.npz` ファイルで保存・再読み込みするための API。
解析の中間結果を軽量・自己完結なファイルとして保存し、再利用・持ち運び・共有ができる。

- 保存: `PyMEA.save_npz(path, dtype="int16")`
- 読込: `read_MEA_npz(path, electrode_distance)`

---

## 基本的な使い方

```python
from pyMEA import read_MEA, read_MEA_npz

# .hed/.bio から必要な区間だけ読み込む
mea = read_MEA("data.hed", start=0, end=5, electrode_distance=450)

# .npz で保存(既定は int16。容量最小)
mea.save_npz("data.npz")

# 再読み込み(サンプリングレート・GAIN・時刻はメタ情報から復元)
mea = read_MEA_npz("data.npz", electrode_distance=450)
```

`read_MEA_npz` は `.hed`/`.bio` を必要とせず、`.npz` 単体で完全に復元できる。

---

## API

### `PyMEA.save_npz(path, dtype="int16")`

| 引数 | 説明 |
|---|---|
| `path` | 保存先パス(`.npz`)。拡張子が無ければ numpy が付与する |
| `dtype` | `"int16"`(既定) / `"float32"` |

電位データのみを保存し、時刻行は保存しない(`start`/`SAMPLING_RATE`/データ長から再生成できるため)。
サンプリングレート・GAIN・start・end・元の `.hed` パスをメタ情報として同梱する。

### `read_MEA_npz(path, electrode_distance)`

| 引数 | 説明 |
|---|---|
| `path` | `.npz` ファイルのパス |
| `electrode_distance` | 電極間距離 (μm) |

戻り値は `read_MEA` と同じ `PyMEA`。以降は通常どおり解析・描画できる。

```python
mea = read_MEA_npz("data.npz", 450)
peak_index = detect_peak_neg(mea.data)
isi = mea.calculator.isi(peak_index, ch=32)
mea.fig.showAll()
```

---

## dtype の選択

| dtype | 精度 | 目安サイズ | 用途 |
|---|---|---|---|
| `"int16"` (既定) | 16bit量子化。誤差 < 半ADC-LSB(測定分解能以下) | 最小(約1/4 + 圧縮) | 通常はこちら |
| `"float32"` | ビット完全一致(無損失) | 小(約1/2 + 圧縮) | 元の値を1ビットも変えたくないとき |

### int16 の損失について

int16 保存は電位を実際の振幅範囲に対して `scale = max(|V|)/32767` で再量子化する。
そのためビット単位では一致しないが、誤差は最大でも `scale/2`(半ステップ)に収まり、
これは**元の測定器の分解能(1 LSB)の半分未満**になる。

実測例(3秒 cardio, GAIN=2000):

| 項目 | 値 |
|---|---|
| int16保存の最大誤差 | 約 0.04 μV |
| 測定器の分解能(1 LSB) | 約 0.15 μV |
| 相対誤差(対 振幅) | 0.0015%(有効数字 約4桁一致) |

誤差は測定器が元々区別できない桁での丸めであり、ピーク検出・ISI・FPD・伝導速度などの
解析結果に実質的な影響はない。**元の生値を厳密に保持したい場合のみ `dtype="float32"` を使う。**

---

## 容量削減の目安

実測(3秒 cardio):

| 形式 | サイズ | 対 float64 |
|---|---|---|
| float64 生(参考) | 15.60 MB | 1.00x |
| `.npz` float32(圧縮込み) | 2.81 MB | **0.18x** |
| `.npz` int16(圧縮込み) | 2.27 MB | **0.15x** |

float32化(半分) + DEFLATE圧縮が重なり、生の float64 比で約 1/5〜1/7 になる。

---

## ユースケース: 区間を切り出して持ち運ぶ

元ファイルが巨大でも、解析対象の区間だけを切り出して軽量な `.npz` として保存・配布できる。
`read_MEA(start, end)` は内部でディスクから該当区間だけを読み込むため、元ファイル全体を
メモリに載せる必要がない。

```python
# 巨大な .bio から「30s〜40s」だけ抜き出す(全体は読まない)
mea = read_MEA("huge_recording.hed", start=30, end=40, electrode_distance=450)

# さらに小数秒で絞り込む場合
mea = mea.from_slice(32.5, 35.0)

# 着目区間だけを自己完結のクリップとして保存
mea.save_npz("clip_32.5-35.0s.npz")
```

`start`/`end` もファイルに記録されるため、「どの区間を切り出したか」が自己記述的に残る。

---

## 仕組みと注意点

- **時刻行は保存しない**: `start`/`SAMPLING_RATE`/データ長から `float64` で再生成する。
  このため `mea[0]` / `mea.times` は常に正確な時刻(float64)を返す(長時間記録でも精度劣化なし)。
- **メタ情報を内包**: SAMPLING_RATE / GAIN / start / end / 元 `.hed` パスを同梱し、1ファイルで完結する。
- **標準フォーマット**: NumPy標準形式のため `np.load("data.npz")` で pyMEA 外でも開ける。
- **位置づけ**: `.npz` は解析・共有用の軽量コピー。生の完全データの一次保管は元の `.hed`/`.bio` を残すのが安全。

### .npz 内のキー(参考)

| キー | 内容 |
|---|---|
| `voltages` | 電位データ (64, N)。int16 または float32 |
| `sampling_rate` / `gain` | サンプリングレート / GAIN |
| `start` / `end` | 読み込み区間 (s) |
| `dtype` / `scale` | 保存dtype / int16復元用の係数 |
| `hed_path` | 元の `.hed` パス |
