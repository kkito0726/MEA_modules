from dataclasses import dataclass, field


@dataclass
class HedPath:
    path: str = field(init=False)

    def __init__(self, hed_path: str):
        if not hed_path.endswith(".hed"):
            raise ValueError(".hedファイルのパスを入力してください")
        self.path = hed_path

    def __repr__(self) -> str:
        return self.path
