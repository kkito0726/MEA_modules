from setuptools import setup, find_packages

setup(
    name="pyMEA",  # パッケージ名（pip listで表示される）
    version="1.3.1",  # バージョン
    description="MEA計測データを読み込み・解析するためのモジュール",  # 説明
    author="kentaro kito",  # 作者名
    packages=find_packages(),  # 使うモジュール一覧を指定する
    license="MIT",  # ライセンス
)
