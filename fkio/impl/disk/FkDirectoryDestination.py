import os as _os

import nicegui.elements.mixins.value_element
from nicegui import ui

from fkio.FkDestination import FkDestination as _FkDestination
from fktasks.FkTask import FkImage as _FkImage


class FkDirectoryDestination(_FkDestination):

    def __init__(self, dst_path: str):
        self._dst_path = _os.path.realpath(dst_path)
        _os.makedirs(self._dst_path, exist_ok=True)

    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        image.save(self._dst_path, image_ext, caption_text_ext)

    @classmethod
    def webui_config(cls):
        with ui.grid()as element:
            output_dirpath = ui.input("Output directory", placeholder="/path/to/input/directory").classes("w-full")

        return element, [output_dirpath]

    @classmethod
    def webui_validate(
            cls,
            output_dirpath: nicegui.elements.mixins.value_element.ValueElement
    ) -> list[bool]:
        return [True if output_dirpath.value.strip() else "Invalid path", True]

    @classmethod
    def webui_info(cls, dst_path: str):
        with ui.element("div") as element:
            with ui.grid(columns=2).style("gap:0 0.2rem; grid-template-columns:min-content min-content;"):
                ui.label("Directory:").classes("text-bold")
                ui.label(dst_path).style("font-family:monospace")

        return element

    @classmethod
    def webui_name(cls) -> str:
        return "File Directory Output"
