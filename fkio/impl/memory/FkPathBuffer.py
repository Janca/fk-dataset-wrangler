import os as _os

import nicegui.element
from nicegui import ui

from fkio.FkDestination import FkDestination as _FkDestination
from fkio.FkSource import FkSource as _FkSource
from fkio.impl.memory.FkBuffer import FkBuffer as _FkBuffer
from fktasks.FkTask import FkImage as _FkImage


class FkPathBuffer(_FkDestination, _FkSource, _FkBuffer):

    def __init__(self, *args, **kwargs):
        self.image_paths: list[str] = []
        super().__init__(*args, **kwargs)
        super(_FkSource, self).__init__(src_path=None, *args, **kwargs)

    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        image_path = _os.path.realpath(image.filepath)
        self.image_paths.append(image_path)

    def yield_next(self) -> _FkImage:
        for image_path in self.image_paths:
            yield _FkImage(image_path)

    @classmethod
    def webui_config(cls, buffers: list[_FkBuffer] = None, *args, **kwargs) -> tuple[
        nicegui.element.Element,
        list[nicegui.element.Element]
    ]:
        if buffers:
            with ui.element("div") as element:
                opts = {buffer: buffer.name for buffer in buffers} if buffers else []
                source_selector = ui.select(
                    label="Available Buffers",
                    options=opts
                )

            return element, [source_selector]

        else:
            return super().webui_config(cls, *args, **kwargs)

    @classmethod
    def webui_name(cls) -> str:
        return "Path Buffer"
