import abc as _abc
import os as _os
from typing import Optional as _Optional

import nicegui.element as _nicegui_element

from fktasks.FkTask import FkImage as _FkImage


class FkSource(_abc.ABC):

    def __init__(self, src_path: _Optional[str]):
        self.src_path = _os.path.realpath(src_path) if src_path else None

    @_abc.abstractmethod
    def yield_next(self) -> _FkImage:
        pass

    @classmethod
    @_abc.abstractmethod
    def webui_pipeline_config(cls) -> tuple[_nicegui_element.Element, list[_nicegui_element.Element]]:
        pass

    @classmethod
    @_abc.abstractmethod
    def webui_pipeline_info(cls, *args):
        pass

    @classmethod
    def friendly_name(cls) -> str:
        return cls.__name__
