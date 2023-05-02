import abc as _abc
import os as _os

from tasks.FkSource import FkSource as _FkSource
from tasks.FkTask import FkImage as _FkImage


class FkDestination(_abc.ABC):
    @_abc.abstractmethod
    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        pass


class FkDirectoryDestination(FkDestination):

    def __init__(self, dst_path: str):
        self._dst_path = _os.path.realpath(dst_path)
        _os.makedirs(self._dst_path, exist_ok=True)

    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        image.save(self._dst_path, image_ext, caption_text_ext)


class FkBuffer(FkDestination, _FkSource):

    def __init__(self):
        self.image_paths: list[str] = []

    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        image_path = _os.path.realpath(image.filepath)
        self.image_paths.append(image_path)

    def iterator(self) -> _FkImage:
        for image_path in self.image_paths:
            yield _FkImage(image_path)
