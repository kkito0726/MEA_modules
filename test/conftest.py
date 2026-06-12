import matplotlib

# テスト実行時にGUIウィンドウを開かないようにする
matplotlib.use("Agg")

# 原本の .hed/.bio を使わず、3秒フィクスチャ(.npz)からデータを供給する
from test.fixtures import install_fixture_io

install_fixture_io()
