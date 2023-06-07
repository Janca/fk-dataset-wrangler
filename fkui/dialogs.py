import collections
from typing import Optional, Callable, Union

import nicegui.element
import nicegui.elements.mixins.text_element
import nicegui.elements.mixins.value_element
from nicegui import ui

import fkui.utils
from fkio.FkDestination import FkDestination
from fkio.FkSource import FkSource
from fkio.impl.memory.FkBuffer import FkBuffer
from fkio.impl.memory.FkPathBuffer import FkPathBuffer
from fktasks.FkTask import FkTask
from shared import FkWebUI

FkButton = collections.namedtuple("FkButton", ["label", "props", "style", "classes"])


def show_fkio_selector(
        fkio_type: str,
        fkio_obj: list[FkSource],
        on_select: Callable[[Union[FkWebUI, FkDestination], list], None]
):
    fkio_type = fkio_type.capitalize()
    selected_fkio: Optional[FkWebUI] = None
    selected_fkio_inputs: Optional[list[nicegui.element.Element]] = None

    def on_confirm():
        if not selected_fkio:
            return False

        if not selected_fkio_inputs:
            on_select(selected_fkio, [])
            return True

        validation = selected_fkio.webui_validate(*selected_fkio_inputs)
        if isinstance(validation, list):
            has_error = False
            for i, fkio_o in enumerate(selected_fkio_inputs):
                source_validation = validation[i]

                if isinstance(source_validation, str) or not source_validation:
                    fkio_o.props(f"error error-message=\"{source_validation}\"")
                    has_error = True

            if has_error:
                return False

        elif not validation:
            return False

        on_select(selected_fkio, fkui.utils.get_values(*selected_fkio_inputs))
        return True

    with show_confirm_dialog(
            title=f"Select {fkio_type} Source",
            props="no-backdrop-dismiss",
            on_confirmation=on_confirm,
            confirm_btn=FkButton(f"Add {fkio_type}", "color=primary flat", None, None)
    ):
        with ui.element("div").style("padding-top:1rem;"):

            def on_fkio_inst_select(event: nicegui.elements.mixins.value_element.ValueChangeEventArguments):
                nonlocal selected_fkio, selected_fkio_inputs

                fkio_inst: FkSource = event.value
                if selected_fkio:
                    selected_fkio_inputs = None
                    source_webui_wrapper.clear()

                with source_webui_wrapper:
                    if not isinstance(fkio_inst, FkPathBuffer):  # hide ui on buffer type input
                        ui.label(f"Configure {fkio_type} Source").classes("mt-4 text-bold")

                        fk_src_webui = fkio_inst.webui_config()
                        if not fk_src_webui:
                            source_webui_wrapper.clear()

                        else:
                            _, selected_fkio_inputs = fk_src_webui

                    selected_fkio = fkio_inst

            ui.select(
                label=f"{fkio_type} Source",
                options={
                    fk_src: (fk_src.webui_name() if not isinstance(fk_src, FkBuffer) else f"Buffer: {fk_src.name}")
                    for fk_src in fkio_obj
                },
                on_change=on_fkio_inst_select
            ).props("options-dense outlined")

            with ui.element("form").props("color=negative") as source_webui_wrapper:
                pass


def show_task_selector(tasks: list[FkTask], on_select=Callable[[FkTask], None]):
    selected_task: Optional[FkTask] = None

    def on_confirm():
        nonlocal selected_task

        if not selected_task:
            return False

        on_select(selected_task)
        return True

    with show_confirm_dialog(
            title="Select Task",
            confirm_btn=FkButton(f"Add Task", "color=primary flat", None, None),
            on_confirmation=on_confirm
    ):
        with ui.element("div").style("padding-top:1rem;"):
            def on_task_select(event: nicegui.elements.mixins.value_element.ValueChangeEventArguments):
                nonlocal selected_task

                selected_task = event.value

            ui.select(
                label="Task",
                options={fk_task: fk_task.webui_name() for fk_task in tasks},
                on_change=on_task_select
            ).props(
                "menu-anchor=\"bottom left\" "
                "options-dense "
                "outlined"
            )


def show_confirm_dialog(
        text: str = None,
        title: str = "Confirm",
        on_confirmation: Callable[[], Optional[bool]] = None,
        on_cancel: Callable[[], None] = None,
        props: str = None,
        style: str = None,
        confirm_btn: FkButton = FkButton(label="Yes", props="color=primary flat", style=None, classes=None),
        cancel_btn: FkButton = FkButton(label="Cancel", props="color=text flat", style=None, classes=None)
):
    with ui.dialog().props(props) as dialog:
        with ui.card().style("min-width:298px;max-width:364px").style(style):
            with ui.element("div").classes("w-full"):
                ui.label(title).style("font-size:1.24rem;font-weight:500;")

                if text:
                    nicegui.elements.mixins.text_element.TextElement(tag="p", text=text).classes("mt-1")

                with ui.element("div").classes("w-full") as inner_content:
                    pass

            with ui.element("div").style(
                    "display:flex;"
                    "flex-flow:row nowrap;"
                    "justify-content:flex-end;"
                    "width:100%;"
                    "gap:0.25rem"
            ):
                def _on_cancel():
                    if on_cancel:
                        on_cancel()

                    dialog.close()

                def _on_confirmation():
                    if not on_confirmation:
                        dialog.close()
                        return

                    confirm_value = on_confirmation()
                    if confirm_value is None or confirm_value:
                        dialog.close()

                ui.button(
                    text=cancel_btn.label,
                    on_click=_on_cancel
                ).props(cancel_btn.props).style(cancel_btn.style).classes(cancel_btn.classes)

                confirm_button = ui.button(
                    text=confirm_btn.label,
                    on_click=_on_confirmation
                ).props(confirm_btn.props).style(confirm_btn.style).classes(confirm_btn.classes)

    dialog.open()
    return inner_content
