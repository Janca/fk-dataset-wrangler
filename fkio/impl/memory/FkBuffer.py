import abc as _abc
from typing import Union as _Union

import nicegui.element
from nicegui import ui

from shared import FkWebUI as _FkWebUI


class FkBuffer(_FkWebUI, _abc.ABC):
    def __init__(self, name: str, *args, **kwargs):
        self.name = name

    @classmethod
    def webui_config(cls, *args, **kwargs) -> tuple[nicegui.element.Element, list[nicegui.element.Element]]:
        with ui.element("div").classes("w-full") as element:
            input_name = ui.input("Buffer Name")

        return element, [input_name]

    @classmethod
    def webui_validate(cls, input_name) -> _Union[bool, list]:
        return [True if input_name.value.strip() else "Invalid path"]

    @classmethod
    def webui_info(cls, name: str):
        with ui.element("div") as element:
            with ui.grid(columns=2):
                ui.label("Buffer Name:").classes("text-bold")
                ui.label(name)

        return element
