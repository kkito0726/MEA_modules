import io
import os
from dataclasses import dataclass

from IPython.display import Image, display
from PIL import Image as PILImage


@dataclass(frozen=True)
class FigImage:
    buf: io.BytesIO

    def display(self):
        display(Image(data=self.buf.getvalue()))

    def save(self, path="./output.png"):
        """画像をファイルに保存（拡張子から形式を自動判別）

        Args:
            path (str): 保存先ファイル名（例: 'output.png', 'figure.jpg'）

        Raises:
            ValueError: 対応していない拡張子が指定された場合
        """
        ext = os.path.splitext(path)[1].lower()
        supported = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG"}

        if ext not in supported:
            raise ValueError(
                f"Unsupported file extension '{ext}'. Supported: {list(supported.keys())}"
            )

        # バッファから画像を読み込み、指定形式で保存
        self.buf.seek(0)
        image = PILImage.open(self.buf).convert("RGB")
        image.save(path, format=supported[ext])

    def _repr_png_(self):
        return self.buf.getvalue()
