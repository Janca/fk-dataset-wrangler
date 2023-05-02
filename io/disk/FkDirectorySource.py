import os as _os

from nicegui import ui

from io.shared import FkSource as _FkSource
from tasks.FkTask import FkImage as _FkImage
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
    def webui_element(cls):
        with ui.element("div") as element:
            pass

        return element
