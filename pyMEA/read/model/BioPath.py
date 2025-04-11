from dataclasses import dataclass


@dataclass(frozen=True)
class BioPath:
    path: str

    def __post_init__(self):
        if not self.path.endswith(".bio"):
            raise ValueError(".bioファイルのパスを入力してください")

    def __repr__(self) -> str:
        return self.path
