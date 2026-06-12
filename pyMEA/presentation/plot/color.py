def normalize_color(color, default_color=None):
    """
    color を標準化して常に list[str | list[float]] のリストにする

    Args:
        color: str | list[str] | list[float] | list[list[float]] | None
        default_color: colorがNoneのときに使うデフォルトカラー

    Returns:
        list[str] | list[list[float]]: 正規化された色リスト
    """
    if color is None:
        # デフォルトカラー
        return [default_color]
    elif isinstance(color, str):
        return [color]
    elif isinstance(color, list):
        # RGB値1セットだけ渡された場合 [0.1, 0.2, 0.3]
        if all(isinstance(c, (int, float)) for c in color):
            return [color]
        # list[str] や list[list[float]] はそのまま
        return color

    else:
        raise TypeError("color must be str or list[str] or list[list[float]]")
