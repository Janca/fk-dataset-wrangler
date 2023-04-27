from typing import Callable as _Callable

import PIL.Image as _Pillow
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


def format_timestamp(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    return "%02d:%02d:%02d" % (hours, minutes % 60, seconds % 60)


def safe_fn(fn: _Callable) -> any:
    try:
        return fn()
    except:
        return None


def resize_image_aspect(image: _PillowImage, max_size: int, copy: bool = True) -> _PillowImage:
    width, height = image.size

    if width > height and width > max_size:
        ratio = height / width

        width = max_size
        height = width * ratio

    elif height > width and height > max_size:
        ratio = width / height

        height = max_size
        width = height * ratio

    elif width == height and width > max_size:
        width = max_size
        height = max_size

    else:
        return image.copy() if copy else image

    width = int(width)
    height = int(height)

    return image.resize(
        size=(width, height),
        resample=_Pillow.LANCZOS
    )
