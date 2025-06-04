import threading
from dataclasses import dataclass
from typing import Optional, Dict

import PIL.Image as _Pillow
from PIL.Image import Image as _PillowImage
import cv2 as _cv2
import numpy as _numpy


@dataclass
class _CacheEntry:
    pillow_image: Optional[_PillowImage] = None
    cv2_image: Optional[_numpy.ndarray] = None
    cv2_gray_image: Optional[_numpy.ndarray] = None
    has_slot: bool = False


class GlobalImageDataCache:
    def __init__(self, max_capacity: int = 32):
        self._semaphore = threading.Semaphore(max_capacity)
        self._entries: Dict[str, _CacheEntry] = {}
        self._entry_locks: Dict[str, threading.Lock] = {}

    def _get_lock(self, filepath: str) -> threading.Lock:
        lock = self._entry_locks.get(filepath)
        if lock is None:
            lock = threading.Lock()
            self._entry_locks[filepath] = lock
        return lock

    def get_pillow_image(self, filepath: str) -> _PillowImage:
        lock = self._get_lock(filepath)
        with lock:
            entry = self._entries.get(filepath)
            if entry is None:
                entry = _CacheEntry()
                self._entries[filepath] = entry
            if entry.pillow_image is None:
                if not entry.has_slot:
                    self._semaphore.acquire()
                    entry.has_slot = True
                temp = _Pillow.open(filepath)
                entry.pillow_image = temp.copy()
                temp.close()
            return entry.pillow_image

    def _pil_to_cv(self, image: _PillowImage) -> _numpy.ndarray:
        mode = image.mode
        if mode == '1':
            new_image = _numpy.array(image, dtype=_numpy.uint8)
            new_image *= 255
        elif mode == 'L':
            new_image = _numpy.array(image, dtype=_numpy.uint8)
        elif mode in ('LA', 'La'):
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
            new_image = _numpy.array(image, dtype=_numpy.uint8)
            new_image = _cv2.cvtColor(new_image, _cv2.COLOR_YCrCb2BGR)
        elif mode in ('P', 'CMYK'):
            new_image = _numpy.array(image.convert('RGB'), dtype=_numpy.uint8)
            new_image = _cv2.cvtColor(new_image, _cv2.COLOR_RGB2BGR)
        elif mode in ('PA', 'Pa'):
            new_image = _numpy.array(image.convert('RGBA'), dtype=_numpy.uint8)
            new_image = _cv2.cvtColor(new_image, _cv2.COLOR_RGBA2BGRA)
        else:
            raise ValueError(f'unhandled image color mode: {mode}')
        return new_image

    def get_cv2_image(self, filepath: str) -> _numpy.ndarray:
        pil_image = self.get_pillow_image(filepath)
        lock = self._get_lock(filepath)
        with lock:
            entry = self._entries[filepath]
            if entry.cv2_image is None:
                entry.cv2_image = self._pil_to_cv(pil_image)
            return entry.cv2_image

    def get_cv2_grayscale_image(self, filepath: str) -> _numpy.ndarray:
        cv_image = self.get_cv2_image(filepath)
        lock = self._get_lock(filepath)
        with lock:
            entry = self._entries[filepath]
            if entry.cv2_gray_image is None:
                entry.cv2_gray_image = _cv2.cvtColor(cv_image, _cv2.COLOR_BGR2GRAY)
            return entry.cv2_gray_image

    def update_pillow_image(self, filepath: str, new_image: _PillowImage):
        lock = self._get_lock(filepath)
        with lock:
            entry = self._entries.get(filepath)
            if entry is None:
                entry = _CacheEntry()
                self._entries[filepath] = entry
            if not entry.has_slot:
                self._semaphore.acquire()
                entry.has_slot = True
            entry.pillow_image = new_image
            entry.cv2_image = None
            entry.cv2_gray_image = None

    def release_image_data(self, filepath: str):
        lock = self._get_lock(filepath)
        with lock:
            entry = self._entries.get(filepath)
            if entry and entry.has_slot:
                if entry.pillow_image is not None:
                    try:
                        entry.pillow_image.close()
                    except Exception:
                        pass
                entry.pillow_image = None
                entry.cv2_image = None
                entry.cv2_gray_image = None
                entry.has_slot = False
                self._semaphore.release()
