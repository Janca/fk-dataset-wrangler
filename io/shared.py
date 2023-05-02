import abc as _abc
import os as _os
from typing import Optional as _Optional

from tasks.FkTask import FkImage as _FkImage


class FkSource(_abc.ABC):

    def __init__(self, src_path: _Optional[str]):
        self.src_path = _os.path.realpath(src_path) if src_path else None

    @_abc.abstractmethod
    def yield_next(self) -> _FkImage:
        pass

    @classmethod
    @_abc.abstractmethod
    def webui_element(cls):
        pass


class FkDestination(_abc.ABC):
    @_abc.abstractmethod
    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        pass
