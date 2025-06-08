import io
import os
from dataclasses import dataclass
from functools import cached_property

import imageio
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


@dataclass(frozen=True)
class VideoMEA:
    fig_images: list[FigImage]

    def __getitem__(self, index: int) -> FigImage:
        return self.fig_images[index]

    def __len__(self) -> int:
        return len(self.fig_images)

    def __iter__(self):
        return iter(self.fig_images)

    @cached_property
    def buf_list(self) -> list[io.BytesIO]:
        return [image.buf for image in self.fig_images]

    @cached_property
    def read_buf_list(self):
        # return [imageio.v2.imread(self._reset(buf)) for buf in self.buf_list]

        # 1. 全画像を読み込んでサイズ収集
        images = []
        widths = []
        heights = []

        for buf in self.buf_list:
            buf.seek(0)
            img = PILImage.open(buf).convert("RGB")
            images.append(img)
            widths.append(img.width)
            heights.append(img.height)

        # 2. 平均サイズを計算
        avg_width = int(sum(widths) / len(widths))
        avg_height = int(sum(heights) / len(heights))
        avg_size = (avg_width, avg_height)

        # 3. 各画像を平均サイズにリサイズ
        resized_images = [img.resize(avg_size, PILImage.BICUBIC) for img in images]
        return resized_images

    def _reset(self, buf: io.BytesIO) -> io.BytesIO:
        buf.seek(0)
        return buf

    def display_gif(self, duration=0.1):
        # GIFをバッファに保存
        gif_buffer = io.BytesIO()
        imageio.mimsave(gif_buffer, self.read_buf_list, format="GIF", duration=duration)
        gif_buffer.seek(0)

        # Jupyter上に表示
        display(Image(data=gif_buffer.getvalue()))

    def save_gif(self, path="./output.gif", duration=0.1):
        ext = os.path.splitext(path)[1].lower()
        if ext != ".gif":
            raise ValueError("拡張子は .gif を指定してください")

        imageio.mimsave(path, self.read_buf_list, format="GIF", duration=duration)

    def save_mp4(self, path="./output.mp4", fps=10):
        ext = os.path.splitext(path)[1].lower()
        if ext != ".mp4":
            raise ValueError("拡張子は .mp4 を指定してください")

        with imageio.get_writer(path, fps=fps, codec="libx264") as writer:
            for frame in self.read_buf_list:
                writer.append_data(frame)
