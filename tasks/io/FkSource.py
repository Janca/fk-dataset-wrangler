import abc as _abc
import os as _os

from tasks.FkTask import FkImage as _FkImage
from utils import KNOWN_IMAGE_EXTENSIONS as _KNOWN_IMAGE_EXTENSIONS


class FkSource(_abc.ABC):

    def __init__(self, src_path: str):
        self.src_path = _os.path.realpath(src_path)

    @_abc.abstractmethod
    def yield_next(self) -> _FkImage:
        pass


class FkDirectorySource(FkSource):
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
