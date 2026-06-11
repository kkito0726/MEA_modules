"""公開APIの互換性を保証する回帰テスト。

pyMEA/__init__.py 経由でインポートできる名前と、その戻り値オブジェクトの
公開メソッド・シグネチャはライブラリ利用者との契約であり、
リファクタリングで変更してはならない。
このテストが落ちた場合は公開APIを壊しているため、実装側を修正すること。
"""

import inspect

import pyMEA
from pyMEA import (
    MEA,
    Calculator,
    FigMEA,
    FilterType,
    MutableMEA,
    VideoMEA,
    detect_peak_all,
    detect_peak_neg,
    detect_peak_pos,
    read_MEA,
)

EXPECTED_ALL = {
    "read_MEA",
    "FilterType",
    "MEA",
    "MutableMEA",
    "FigMEA",
    "VideoMEA",
    "Calculator",
    "detect_peak_neg",
    "detect_peak_pos",
    "detect_peak_all",
}


def param_names(func) -> list[str]:
    return list(inspect.signature(func).parameters.keys())


def test_all_exports_unchanged():
    assert set(pyMEA.__all__) == EXPECTED_ALL


def test_read_MEA_signature():
    assert param_names(read_MEA) == [
        "hed_path",
        "start",
        "end",
        "electrode_distance",
        "filter_type",
        "front",
        "back",
        "distance",
        "power_noise_freq",
        "steps",
    ]
    defaults = {
        name: p.default
        for name, p in inspect.signature(read_MEA).parameters.items()
        if p.default is not inspect.Parameter.empty
    }
    assert defaults == {
        "filter_type": FilterType.NONE,
        "front": 0.05,
        "back": 0.3,
        "distance": 3000,
        "power_noise_freq": 50,
        "steps": 10,
    }


def test_filter_type_members():
    assert {m.name for m in FilterType} >= {"NONE", "CARDIO_AVE_WAVE", "FILTER_MEA"}


def test_detect_peak_signatures():
    expected = ["MEA_data", "distance", "threshold", "min_amp", "prominence", "width"]
    assert param_names(detect_peak_neg) == expected
    assert param_names(detect_peak_pos) == expected
    assert param_names(detect_peak_all) == [
        "MEA_data",
        "threshold",
        "distance",
        "min_amp",
        "prominence",
        "width",
    ]


def test_pymea_facade_contract():
    """read_MEA の戻り値 PyMEA の公開フィールド・メソッドを保証する。"""
    pymea_cls = inspect.signature(read_MEA).return_annotation
    assert pymea_cls.__name__ == "PyMEA"

    fields = pymea_cls.__dataclass_fields__
    assert set(fields.keys()) >= {"data", "electrode", "fig", "calculator"}

    assert param_names(pymea_cls.from_slice) == ["self", "start", "end"]
    assert param_names(pymea_cls.from_beat_cycles) == [
        "self",
        "peak_index",
        "base_ch",
        "margin_time",
    ]
    assert param_names(pymea_cls.init_time) == ["self"]
    assert param_names(pymea_cls.down_sampling) == ["self", "down_sampling_rate"]
    assert param_names(pymea_cls.iirnotch_filter) == ["self", "filter_hz", "Q"]
    for dunder in ("__getitem__", "__len__", "__iter__", "__add__", "__sub__"):
        assert hasattr(pymea_cls, dunder)


def test_mea_contract():
    fields = MEA.__dataclass_fields__
    assert set(fields.keys()) == {
        "hed_path",
        "start",
        "end",
        "SAMPLING_RATE",
        "GAIN",
        "array",
    }
    assert param_names(MEA.from_slice) == ["self", "start_frame", "end_frame"]
    assert param_names(MEA.from_beat_cycles) == [
        "self",
        "peak_index",
        "base_ch",
        "margin_time",
    ]
    assert param_names(MEA.down_sampling) == ["self", "down_sampling_rate"]
    assert param_names(MEA.iirnotch_filter) == ["self", "filter_hz", "Q"]
    for name in ("info", "shape", "init_time", "__getitem__", "__len__"):
        assert hasattr(MEA, name)
    assert param_names(MutableMEA.__init__) == ["self", "hed_path", "start", "end"]


def test_calculator_contract():
    for method in ("isi", "fpd", "conduction_velocity", "distance", "gradient_velocity"):
        assert callable(getattr(Calculator, method)), method


def test_figmea_contract():
    for method in (
        "plot_spectrum",
        "showAll",
        "showSingle",
        "plotPeaks",
        "showDetection",
        "raster_plot",
        "mkHist",
        "draw_2d",
        "draw_3d",
        "draw_line_conduction",
    ):
        assert callable(getattr(FigMEA, method)), method


def test_video_mea_contract():
    for method in ("display_gif", "save_gif", "save_mp4", "__getitem__", "__len__"):
        assert hasattr(VideoMEA, method), method


def test_value_objects_contract():
    """Calculator の戻り値 (ISI, FPD, ConductionVelocity) の公開メソッドを保証する。"""
    from pyMEA.calculator.values.ConductionVelocity import ConductionVelocity
    from pyMEA.calculator.values.FPD import FPD
    from pyMEA.calculator.values.ISI import ISI

    for cls in (ISI, FPD, ConductionVelocity):
        for name in ("mean", "std", "se", "stv", "coefficient_of_variation"):
            assert hasattr(cls, name), f"{cls.__name__}.{name}"
        for dunder in ("__getitem__", "__len__", "__eq__", "__lt__"):
            assert hasattr(cls, dunder), f"{cls.__name__}.{dunder}"

    assert callable(getattr(ISI, "show"))
    assert callable(getattr(FPD, "show"))


def test_peaks64_contract():
    """detect_peak_* の戻り値 Peaks64 系の公開メソッドを保証する。"""
    from pyMEA.find_peaks.peak_model import AllPeaks64, NegPeaks64, Peaks64, PosPeaks64

    for cls in (Peaks64, NegPeaks64, PosPeaks64, AllPeaks64):
        for dunder in ("__getitem__", "__len__", "__iter__"):
            assert hasattr(cls, dunder), f"{cls.__name__}.{dunder}"
