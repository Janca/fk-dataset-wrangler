import os as _os

from nicegui import ui

from fkio.FkSource import FkSource as _FkSource
from fktasks.FkTask import FkImage as _FkImage
from utils import KNOWN_IMAGE_EXTENSIONS as _KNOWN_IMAGE_EXTENSIONS


class FkDirectorySource(_FkSource):
    def __init__(self, src_path: str, recursive: bool = True):
        self.recursive = recursive
        super().__init__(src_path)

    def yield_next(self) -> _FkImage:
        def scan_dir(path: str):
            for file_entry in _os.scandir(path):
                if file_entry.is_dir() and self.recursive:
                    yield from scan_dir(file_entry.path)
                    continue

                file_ext = _os.path.splitext(file_entry.name)[1]
                if file_ext in _KNOWN_IMAGE_EXTENSIONS:
                    yield _FkImage(file_entry.path)

        yield from scan_dir(self.src_path)

    @classmethod
    def webui_pipeline_config(cls):
        with ui.grid().style() as element:
            input_dirpath = ui.input("Input directory", placeholder="/path/to/input/directory").classes("w-full")
            recursive = ui.checkbox("Include subdirectories", value=True).classes().props("left-label")

        return element, [input_dirpath, recursive]

    @classmethod
    def webui_pipeline_info(cls, src_path: str, recursive: bool):
        with ui.element("div") as element:
            with ui.grid(columns=2).style("gap:0 0.2rem"):
                ui.label("Directory:").classes("text-bold")
                ui.label(src_path)

                ui.label("Recursive:").classes("text-bold")
                ui.label(str(recursive))

        return element

    @classmethod
    def friendly_name(cls) -> str:
        return "File Directory Input"


