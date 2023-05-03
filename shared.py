import abc as _abc
from typing import Union

import nicegui.element


class FkWebUI(_abc.ABC):

    @classmethod
    @_abc.abstractmethod
    def webui_config(cls, *args, **kwargs) -> tuple[nicegui.element.Element, list[nicegui.element.Element]]:
        pass

    @classmethod
    @_abc.abstractmethod
    def webui_validate(cls, *args, **kwargs) -> Union[bool, list]:
        pass

    @classmethod
    @_abc.abstractmethod
    def webui_info(cls, *args, **kwargs):
        pass

    @classmethod
    def webui_name(cls) -> str:
        return cls.__name__
