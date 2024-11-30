from pathlib import Path


def get_resource_path(filename: str) -> Path:
    """リソースファイルへの絶対パスを取得"""
    project_root = Path(__file__).resolve().parents[1]
    resources_path = project_root / "test" / "resources"

    resource_file = resources_path / filename
    if not resource_file.exists():
        raise FileNotFoundError(f"Resource not found: {resource_file}")
    return resource_file
