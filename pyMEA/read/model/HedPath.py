from dataclasses import dataclass


@dataclass(frozen=True)
class HedPath:
    path: str  # init=True がデフォルトなので明示しなくてOK

    def __post_init__(self):
        if not self.path.endswith(".hed"):
            raise ValueError(".hedファイルのパスを入力してください")

    def __repr__(self) -> str:
        return self.path
