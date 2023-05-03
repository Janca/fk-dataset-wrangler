import os as _os

from fkio.FkDestination import FkDestination as _FkDestination
from fktasks.FkTask import FkImage as _FkImage


class FkDirectoryDestination(_FkDestination):

    def __init__(self, dst_path: str):
        self._dst_path = _os.path.realpath(dst_path)
        _os.makedirs(self._dst_path, exist_ok=True)

    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        image.save(self._dst_path, image_ext, caption_text_ext)
