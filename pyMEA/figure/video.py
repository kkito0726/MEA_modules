import io
import os
from dataclasses import dataclass
from functools import cached_property

import imageio
from IPython.display import Image, display


@dataclass(frozen=True)
class VideoMEA:
    buf_list: list[io.BytesIO]

    @cached_property
    def read_buf_list(self):
        return [imageio.v2.imread(buf) for buf in self.buf_list]

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
