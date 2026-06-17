"""テスト用フィクスチャI/O。

原本の .hed/.bio はリポジトリに置かず、3秒ぶんを抽出した .npz
(test/resources/fixtures/*.npz) からデータを供給する。

read_MEA / hed2array が内部で呼ぶ decode_hed・read_bio を
フィクスチャ駆動に差し替えることで、テストは read_MEA を通常どおり
呼び出せる(ファイルI/O層のロジックも経由する)。
"""

import os
from functools import lru_cache
from pathlib import Path

import numpy as np

_FIXTURE_DIR = Path(__file__).resolve().parent / "resources" / "fixtures"

# 論理 .hed 名 / 原本ファイル名 -> フィクスチャ名 の対応
_NAME_MAP = {
    "cardio.hed": "cardio",
    "neuro.hed": "neuro",
    "230615_day2_test_5s_.hed": "cardio",
    "1102_dish3_day10_p210_5sec_.hed": "neuro",
}


def fixture_hed_path(name: str) -> str:
    """テストが read_MEA に渡す論理 .hed パスを返す (実ファイルは不要)。"""
    return f"{name}.hed"


def fixture_npz_path(name: str) -> str:
    """read_MEA_npz で直接読み込む実フィクスチャ .npz の絶対パスを返す。"""
    return str(_FIXTURE_DIR / f"{name}.npz")


@lru_cache(maxsize=None)
def _load_npz(name: str):
    # フィクスチャは read_MEA_npz で読める正規形式(.npz)。公開API経由で実ファイルを読む。
    from pyMEA import read_MEA_npz

    mea = read_MEA_npz(str(_FIXTURE_DIR / f"{name}.npz")).data
    return mea.array, int(mea.SAMPLING_RATE), int(mea.GAIN)


def _fixture_name(path) -> str | None:
    base = os.path.basename(str(path))
    if base in _NAME_MAP:
        return _NAME_MAP[base]
    # bio パス ("cardio0001.bio" / "230615..._0001.bio") に対応
    for hed_name, fixture in _NAME_MAP.items():
        stem = hed_name[:-4]  # ".hed" を除去
        if base == f"{stem}0001.bio":
            return fixture
    return None


_installed = False


def install_fixture_io() -> None:
    """decode_hed / read_bio をフィクスチャ駆動へ差し替える (セッション全体に適用)。"""
    global _installed
    if _installed:
        return
    _installed = True

    from pyMEA.application import read_MEA as read_mea_mod
    from pyMEA.domain.model.HedData import HedData
    from pyMEA.infrastructure import read_bio as read_bio_mod

    _orig_decode_hed = read_bio_mod.decode_hed
    _orig_read_bio = read_bio_mod.read_bio

    def fake_decode_hed(hed_path):
        name = _fixture_name(getattr(hed_path, "path", hed_path))
        if name is None:
            return _orig_decode_hed(hed_path)
        _, sampling_rate, gain = _load_npz(name)
        return HedData(SAMPLING_RATE=sampling_rate, GAIN=gain)

    def fake_read_bio(bio_path, start, end, sampling_rate=10000, gain=50000, volt_range=100):
        name = _fixture_name(getattr(bio_path, "path", bio_path))
        if name is None:
            return _orig_read_bio(bio_path, start, end, sampling_rate, gain, volt_range)
        array, sr, _ = _load_npz(name)
        # 電位値は float32 のまま (検出結果に影響なし)、配列は float64 に揃える
        sliced = array[:, int(start * sr):int(end * sr)].astype(np.float64)
        # 時刻行は float32 だと精度不足になるため正確に再計算する
        sliced[0] = np.arange(sliced.shape[1]) / sr + start
        return sliced

    # read_bio モジュール内 (hed2array が参照)
    read_bio_mod.decode_hed = fake_decode_hed
    read_bio_mod.read_bio = fake_read_bio
    # read_MEA が import 済みの参照
    read_mea_mod.decode_hed = fake_decode_hed
