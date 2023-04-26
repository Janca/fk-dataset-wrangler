import abc as _abc
import os as _os
from typing import Optional as _Optional

import PIL.Image as _Pillow
from PIL.Image import Image as _PillowImage

import utils
from utils import KNOWN_CAPTION_TEXT_EXTENSIONS as _KNOWN_CAPTION_TEXT_EXTENSIONS


class FkImage:
    def __init__(self, filepath: str, image: _PillowImage = None, caption_text: str = None):
        self.filepath = filepath

        self._image = image
        self._working_image = None
        self._cv2_image = None

        self._caption_text = caption_text

    @property
    def image(self) -> _PillowImage:
        if not self._working_image:
            if not self._image:
                self._image = _Pillow.open(self.filepath)

            return self._image

        return self._working_image

    @image.setter
    def image(self, image: _PillowImage):
        self._working_image = image
        self._cv2_image = None

    @property
    def cv2_image(self):
        if not self._cv2_image:
            self._cv2_image = utils.pil2cv(self.image)

        return self._cv2_image

    @property
    def caption_text(self):
        if not self._caption_text:
            image_filename = self.filename
            parent_dirpath = self.dirname

            for caption_text_ext in _KNOWN_CAPTION_TEXT_EXTENSIONS:
                caption_text_filepath = _os.path.join(parent_dirpath, image_filename + caption_text_ext)
                if _os.path.exists(caption_text_filepath):
                    with open(caption_text_filepath, "r", encoding="utf-8", errors="ignore") as caption_file:
                        caption_text = caption_file.read()
                        self._caption_text = caption_text.strip()

        return self._caption_text

    @caption_text.setter
    def caption_text(self, caption_text: str):
        self._caption_text = caption_text

    @property
    def dirname(self) -> str:
        return _os.path.dirname(self.filepath)

    @property
    def basename(self) -> str:
        return _os.path.basename(self.filepath)

    @property
    def extension(self) -> str:
        return _os.path.splitext(self.basename)[1]

    @property
    def filename(self) -> str:
        return _os.path.splitext(self.basename)[0]

    def close(self):
        def close_image(image: _Optional[_PillowImage]):
            if image:
                try:
                    image.close()
                except:
                    pass

        close_image(self._image)
        close_image(self._working_image)


class FkTask(_abc.ABC):
    @_abc.abstractmethod
    def process(self, image: FkImage) -> bool:
        pass
