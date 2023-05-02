import os as _os

from io.shared import FkSource as _FkSource, FkDestination as _FkDestination
from tasks.FkTask import FkImage as _FkImage


class FkPathBuffer(_FkDestination, _FkSource):

    def __init__(self):
        self.image_paths: list[str] = []
        super().__init__(src_path=None)

    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        image_path = _os.path.realpath(image.filepath)
        self.image_paths.append(image_path)

    def iterator(self) -> _FkImage:
        for image_path in self.image_paths:
            yield _FkImage(image_path)
