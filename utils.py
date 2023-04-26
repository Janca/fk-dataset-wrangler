import cv2 as _cv2
import numpy as _numpy
from PIL.Image import Image as _PillowImage

KNOWN_IMAGE_EXTENSIONS = [
    ".bmp",
    ".gif",
    ".jpg",
    ".jpeg",
    ".png",
    ".tiff",
    ".webp"
]

KNOWN_CAPTION_TEXT_EXTENSIONS = [
    ".txt",
    ".caption"
]


# noinspection PyTypeChecker,PyUnresolvedReferences
def pil2cv(image: _PillowImage) -> _numpy.ndarray:
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
