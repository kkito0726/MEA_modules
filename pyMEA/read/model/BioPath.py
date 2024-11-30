from dataclasses import dataclass, field


@dataclass
class BioPath:
    path: str = field(init=False)

    def __init__(self, bio_path: str):
        if not bio_path.endswith(".bio"):
            raise ValueError(".bioファイルのパスを入力してください")
        self.path = bio_path

    def __repr__(self) -> str:
        return self.path
