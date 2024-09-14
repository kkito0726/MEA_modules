from setuptools import find_packages, setup

# requirements.txtを読み込む関数
def parse_requirements(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

setup(
    name="pyMEA",  # パッケージ名（pip listで表示される）
    version="2.9.1",  # バージョン
    description="MEA計測データを読み込み・解析するためのモジュール",  # 説明
    author="kentaro kito",  # 作者名
    packages=find_packages(exclude=["test", "test.*"]),
    install_requires=parse_requirements('requirements.txt'),
    license="MIT",  # ライセンス
)
