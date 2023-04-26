import abc as _abc
import hashlib as _hashlib
import os as _os
from typing import Optional as _Optional

import PIL.Image as _Pillow
import cv2 as _cv2
import numpy as _numpy
from PIL.Image import Image as _PillowImage

from utils import KNOWN_CAPTION_TEXT_EXTENSIONS as _KNOWN_CAPTION_TEXT_EXTENSIONS


class FkImage:
    def __init__(self, filepath: str, image: _PillowImage = None, caption_text: str = None):
        self.filepath = filepath

        self._image = image
        self._cv2_image = None

        self._caption_text = caption_text

    @property
    def image(self) -> _PillowImage:
        if not self._image:
            temp_image = _Pillow.open(self.filepath)
            self._image = temp_image.copy()
            temp_image.close()

        return self._image

    @image.setter
    def image(self, image: _PillowImage):
        self._image = image
        self._cv2_image = None

    @property
    def cv2_image(self):
        # noinspection PyTypeChecker,PyUnresolvedReferences
        def pil_to_cv(image: _PillowImage) -> _numpy.ndarray:
            """
            Credits: https://gist.github.com/panzi/1ceac1cb30bb6b3450aa5227c02eedd3
            :param image: Pillow image
            :return: numpy array for cv2
            """

            mode = image.mode
            new_image: _numpy.ndarray
            if mode == '1':
                new_image = _numpy.array(image, dtype=_numpy.uint8)
                new_image *= 255
            elif mode == 'L':
                new_image = _numpy.array(image, dtype=_numpy.uint8)
            elif mode == 'LA' or mode == 'La':
                new_image = _numpy.array(image.convert('RGBA'), dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_RGBA2BGRA)
            elif mode == 'RGB':
                new_image = _numpy.array(image, dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_RGB2BGR)
            elif mode == 'RGBA':
                new_image = _numpy.array(image, dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_RGBA2BGRA)
            elif mode == 'LAB':
                new_image = _numpy.array(image, dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_LAB2BGR)
            elif mode == 'HSV':
                new_image = _numpy.array(image, dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_HSV2BGR)
            elif mode == 'YCbCr':
                # XXX: not sure if YCbCr == YCrCb
                new_image = _numpy.array(image, dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_YCrCb2BGR)
            elif mode == 'P' or mode == 'CMYK':
                new_image = _numpy.array(image.convert('RGB'), dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_RGB2BGR)
            elif mode == 'PA' or mode == 'Pa':
                new_image = _numpy.array(image.convert('RGBA'), dtype=_numpy.uint8)
                new_image = _cv2.cvtColor(new_image, _cv2.COLOR_RGBA2BGRA)
            else:
                raise ValueError(f'unhandled image color mode: {mode}')

            return new_image

        if not self._cv2_image:
            self._cv2_image = pil_to_cv(self.image)

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

    def save(self, output_dirpath: str, image_ext: str, caption_text_ext: str):
        filename_hash = _hashlib.sha256(self.basename.encode("utf-8")).hexdigest()

        save_image_filepath = _os.path.join(
            output_dirpath,
            filename_hash + image_ext
        )

        self.image.save(save_image_filepath, quality=95 if image_ext in [".jpg", ".jpeg"] else None)
        self.close()

        if self.caption_text:
            caption_text_filename = filename_hash + caption_text_ext
            save_caption_text_filepath = _os.path.join(output_dirpath, caption_text_filename)

            with open(
                    save_caption_text_filepath,
                    "w+",
                    encoding="utf-8",
                    errors="ignore"
            ) as caption_file:
                caption_file.write(self.caption_text)

    def close(self):
        def close_image(image: _Optional[_PillowImage]):
            if image:
                try:
                    image.close()
                except:
                    pass

        if self._image is not None:
            close_image(self._image)

    def destroy(self):
        self.close()

        self.filepath = None
        self._caption_text = None
        self._cv2_image = None
        self._image = None


class FkTask(_abc.ABC):
    @_abc.abstractmethod
    def process(self, image: FkImage) -> bool:
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__


class FkReportableTask(FkTask, _abc.ABC):
    @_abc.abstractmethod
    def report(self) -> list[tuple[str, any]]:
        pass
