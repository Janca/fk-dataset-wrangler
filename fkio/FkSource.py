import abc as _abc
import os as _os
from typing import Optional as _Optional

from fktasks.FkTask import FkImage as _FkImage
from shared import FkWebUI as _FkWebUI


class FkSource(_FkWebUI, _abc.ABC):

    def __init__(self, src_path: _Optional[str]):
        self.src_path = _os.path.realpath(src_path) if src_path else None

    @_abc.abstractmethod
    def yield_next(self) -> _FkImage:
        pass
