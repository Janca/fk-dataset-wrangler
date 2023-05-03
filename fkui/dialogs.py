import collections
from typing import Optional, Callable

import nicegui.element
import nicegui.elements.mixins.text_element
import nicegui.elements.mixins.value_element
from nicegui import ui

import fkui.utils
from fkio.FkSource import FkSource

FkButton = collections.namedtuple("FkButton", ["label", "props", "style", "classes"])


def show_source_selector(fk_sources: list[FkSource], on_select: Callable[[FkSource, list], None]):
    selected_source: Optional[FkSource] = None
    selected_source_inputs: Optional[list[nicegui.element.Element]] = None

    def on_confirm():
        if not selected_source:
            return False

        if not selected_source_inputs:
            return False

        validation = selected_source.webui_validate(*selected_source_inputs)
        if isinstance(validation, list):
            has_error = False
            for i, source_input in enumerate(selected_source_inputs):
                source_validation = validation[i]

                if isinstance(source_validation, str) or not source_validation:
                    source_input.props(f"error error-message=\"{source_validation}\"")
                    has_error = True

            if has_error:
                return False

        elif not validation:
            return False

        on_select(selected_source, fkui.utils.get_values(*selected_source_inputs))

    with show_confirm_dialog(
            title="Select Input Source",
            props="no-backdrop-dismiss",
            on_confirmation=on_confirm,
            confirm_btn=FkButton("Add Input", "color=primary flat", None, None)
    ):
        with ui.element("div"):

            def on_source_select(event: nicegui.elements.mixins.value_element.ValueChangeEventArguments):
                nonlocal selected_source, selected_source_inputs

                fk_src: FkSource = event.value
                if selected_source:
                    source_webui_wrapper.clear()

                with source_webui_wrapper:
                    ui.label("Configure Input Source").classes("mt-4 text-bold")

                    fk_src_webui = fk_src.webui_config()
                    if not fk_src_webui:
                        source_webui_wrapper.clear()

                    else:
                        _, selected_source_inputs = fk_src_webui

                    selected_source = fk_src

            ui.select(
                label="Input Source",
                options={fk_src: fk_src.webui_name() for fk_src in fk_sources},
                on_change=on_source_select
            )

            with ui.element("form").props("color=negative") as source_webui_wrapper:
                pass


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
