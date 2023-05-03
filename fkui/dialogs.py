from typing import Callable as _Callable, Optional

import nicegui.elements.mixins.value_element
from nicegui import ui


def show_source_selector(src_classes: list, on_select: _Callable[[any, ...], None] = None):
    with ui.dialog().props("no-backdrop-dismiss") as dialog, ui.card().style("min-width:368px"):
        with ui.element("div"):
            ui.label("Pipeline Input Source").style("font-size:1.6rem")

        selected_index = -1
        form_elements: Optional[list] = None
        previous_source_ui_element = None

        def show_source_ui(src_index: int):
            nonlocal previous_source_ui_element, selected_index, form_elements

            if previous_source_ui_element is not None:
                source_ui_elem.remove(previous_source_ui_element)

            src_cls = src_classes[src_index]
            selected_index = src_index

            with source_ui_elem:
                src_webui = src_cls.webui_pipeline_config()
                previous_source_ui_element, form_elements = src_webui

        source_selector = ui.select(
            options=[cls.friendly_name() for cls in src_classes],
            label="Input Source"
        ).classes("w-full")

        source_ui_elem = ui.element("div").classes("w-full")
        source_selector.on("update:model-value", lambda event: show_source_ui(event["args"]["value"]))

        def on_click_okay():
            if form_elements is None or selected_index == -1:
                return

            values = [
                it.value for it in form_elements
                if isinstance(it, nicegui.elements.mixins.value_element.ValueElement)
            ]

            try:
                if on_select:
                    selected_src = src_classes[selected_index]
                    on_select(selected_src, values)

            except:
                pass

            finally:
                dialog.close()

        with ui.element("div").style("display:flex; justify-content:flex-end").classes("w-full"):
            ui.button("Cancel", on_click=dialog.close).props("color=text flat")
            ui.button("Okay", on_click=on_click_okay).props("flat").bind_enabled_from(source_selector, "value")

    dialog.open()
