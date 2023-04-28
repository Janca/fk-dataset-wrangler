import importlib as _importlib
import inspect as _inspect
import os as _os
import shutil as _shutil
import sys as _sys
import urllib.request as _urllib_request
import warnings
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


def safe_fn(fn: _Callable, default_value: any = None) -> any:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return fn()
    except:
        return default_value


def resize_image_aspect(image: _PillowImage, max_size: int) -> _PillowImage:
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
        return image.copy()

    width = int(width)
    height = int(height)

    return image.resize(
        size=(width, height),
        resample=_Pillow.LANCZOS
    )


def download_file(url: str, dst: str) -> bool:
    try:
        with _urllib_request.urlopen(url) as response, open(dst, "wb") as dst_file:
            _shutil.copyfileobj(response, dst_file)

        return True

    except:
        return False


def _load_modules_from_directory(directory, parent_package=None):
    """
    Method provided by Google Bard <3
    :param directory:
    :param parent_package:
    :return:
    """
    modules = []

    directory_path = _os.path.abspath(directory)
    if directory_path not in _sys.path:
        _sys.path.append(directory_path)

    for entry in _os.listdir(directory):
        entry_path = _os.path.join(directory, entry)

        if _os.path.isfile(entry_path) and entry.endswith(".py") and not entry.startswith("__"):
            module_name = entry[:-3]

            if parent_package:
                full_module_name = f"{parent_package}.{module_name}"
            else:
                full_module_name = module_name

            module = _importlib.import_module(full_module_name)
            modules.append(module)

        elif _os.path.isdir(entry_path) and _os.path.isfile(_os.path.join(entry_path, "__init__.py")):
            package_name = entry
            if parent_package:
                full_package_name = f"{parent_package}.{package_name}"
            else:
                full_package_name = package_name

            sub_modules = _load_modules_from_directory(entry_path, full_package_name)
            modules.extend(sub_modules)

    return modules


def get_classes_from_module(module):
    """
    Method provided by Google Bard
    :param module:
    :return:
    """
    classes = []

    for name, obj in _inspect.getmembers(module):
        if _inspect.isclass(obj) and obj.__module__ == module.__name__:
            classes.append(obj)

    return classes


def load_modules_and_classes_from_directory(directory, parent_package=None):
    """
    Method provided by Google Bard
    :param directory:
    :param parent_package:
    :return:
    """
    modules = _load_modules_from_directory(directory, parent_package)
    classes = []

    for module in modules:
        module_classes = get_classes_from_module(module)
        classes.extend(module_classes)

    return modules, classes
