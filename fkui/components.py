from typing import Callable as _Callable, Callable, Optional

from nicegui import ui
from nicegui.elements.mixins.value_element import ValueElement

import fkui.dialogs
from fkio.FkDestination import FkDestination as _FkDestination
from fkio.FkSource import FkSource as _FkSource
from fktasks.FkTask import FkTask


def fk_card(title: str, on_delete: _Callable[[...], None] = None):
    with ui.element("div").style("position:relative;width:100%;"):
        ui.badge(title).style(
            "z-index:100;"
            "font-size:0.725rem;"
            "font-weight:500;"
            "line-height:1rem;"
            "left:0.6rem;"
            "top:-0.65rem;"
            "padding:0.25rem 0.5rem"
        ).classes("absolute")

        with ui.card().style(
                "min-height:64px;"
                "width:100%;"
                "position:relative;"
                "font-size:0.825rem;"
        ):
            if on_delete:
                ui.button(
                    on_click=on_delete
                ).props(
                    "icon=delete "
                    "flat "
                    "color=negative "
                    "size=sm "
                    "dense "
                    ""
                ).style(
                    "position:absolute;"
                    "bottom:0;"
                    "right:0;"
                    "z-index:100;"
                    "margin-right:0.25rem;"
                    "margin-bottom:0.25rem"
                )

            return ui.element("div").style("margin-top:0.35rem;").classes("w-full")


def fk_pipeline(
        index: int,
        pipeline_config,
        fk_tasks: list[FkTask],
        fk_sources: list[_FkSource],
        fk_destinations: list[_FkSource],
        name: str = None,
        on_delete: Callable[[int, ...], None] = None
):
    name = f"New Pipeline {index + 1}" if name is None else name
    with ui.expansion().props(
            "group=pipeline expand-icon-toggle"
    ).classes("w-full") as expansion:
        with expansion.add_slot("header"):
            with ui.row().style("min-height:100%;width:100%;align-items:center;"):
                ui.icon("filter_list").style("font-size:1.48rem;margin-right:0.4rem;")
                header_text = ui.label(name).style("font-size:1rem;font-weight:500;")
                pipeline_name_input: Optional[ValueElement] = None

                def on_edit_dialog_confirm():
                    nonlocal name
                    value = pipeline_name_input.value.strip()

                    if not value:
                        pipeline_name_input.props("error error-message=\"Invalid name\"")
                        return False

                    name = pipeline_name_input.value

                    header_text.text = name
                    header_text.update()

                    return True

                def show_edit_dialog():
                    nonlocal pipeline_name_input

                    with fkui.dialogs.show_confirm_dialog(
                            title=f"Edit Pipeline '{name}'",
                            on_confirmation=on_edit_dialog_confirm,
                            confirm_btn=fkui.dialogs.FkButton(
                                label="Save",
                                props="color=primary flat",
                                style=None,
                                classes=None
                            )
                    ):
                        pipeline_name_input = ui.input("Pipeline Name", value=name).props("autofocus")

                with ui.element("div").style("justify-self:flex-end;margin-left:auto;"):
                    ui.button(
                        on_click=show_edit_dialog
                    ).props(
                        "icon=edit "
                        "flat "
                        "color=amber "
                        "size=sm "
                        "dense "
                        ""
                    ).style("margin-right:0.2rem;")
                    ui.button(
                        on_click=lambda: fkui.dialogs.show_confirm_dialog(
                            text=f"Are you sure you want to delete pipeline '{name}'?",
                            title="Delete Pipeline",
                            on_confirmation=on_delete
                        )
                    ).props(
                        "icon=delete "
                        "flat "
                        "color=negative "
                        "size=sm "
                        "dense "
                        ""
                    ).style("margin-right:0.2rem;")

        with ui.grid(rows=3).style("padding:1rem 0; gap:1rem;grid-template-rows:auto 1fr;"):
            with ui.element("div"):
                with ui.element("div").classes("w-full") as source_container:
                    pass

                def create_source_webui_config_info(fk_source: _FkSource, values):
                    def on_source_delete():
                        def on_confirmation():
                            source_container.clear()

                            source_action_container.visible = True
                            source_action_container.update()

                        fkui.dialogs.show_confirm_dialog(
                            text=f"Are you sure you want to delete input source '{fk_source.webui_name()}'?",
                            title="Delete Input",
                            on_confirmation=on_confirmation,
                            props="no-backdrop-dismiss"
                        )

                    with source_container:
                        source_name = fk_source.webui_name()

                        with fk_card(source_name, on_delete=on_source_delete):
                            source_action_container.visible = False
                            source_action_container.update()

                            fk_source.webui_info(*values)

                def show_source_selector():
                    fkui.dialogs.show_fkio_selector("input", fk_sources, on_select=create_source_webui_config_info)

                with ui.element("div").classes("w-full") as source_action_container:
                    ui.button(
                        text="Input",
                        on_click=show_source_selector
                    ).style(
                        "min-height:48px;"
                        "width:100%;"
                    ).props("icon=input outline")

            with ui.element("div"):
                def create_task_webui(task: FkTask):
                    task_name = task.webui_name()

                    def on_task_delete():
                        def on_confirmation():
                            pass

                        fkui.dialogs.show_confirm_dialog(
                            text=f"Are you sure you want to delete task '{task_name}'?",
                            title="Delete Task",
                            on_confirmation=on_confirmation
                        )

                        pass

                    if not task_container.visible:
                        task_container.visible = True
                        task_container.update()

                    with task_list_container:
                        with fk_card(task_name, on_delete=on_task_delete):
                            task_webui = task.webui_config()
                            if not task_webui:
                                ui.label("No configurable options").style("font-weight:500;")

                            else:
                                _, task_inputs = task_webui

                def show_task_selector():
                    fkui.dialogs.show_task_selector(fk_tasks, on_select=create_task_webui)

                with ui.element("div").classes("w-full") as task_container:
                    task_container.visible = False
                    _fk_separator("Tasks")

                    with ui.element("div").style(
                            "display:flex;"
                            "flex-flow:column nowrap;"
                            "gap:1.25rem;"
                            "margin-bottom:1rem;"
                    ).classes("w-full") as task_list_container:
                        pass

                with ui.element("div").classes("w-full") as task_action_container:
                    ui.button(
                        text="Add Task",
                        on_click=show_task_selector
                    ).style(
                        "min-height:48px;"
                        "width:100%;"
                    ).props("icon=add_task outline")

            with ui.element("div"):
                with ui.element("div").classes("w-full") as output_container:
                    pass

                def create_destination_webui_config_info(fk_destination: _FkDestination, values):
                    dst_name = fk_destination.webui_name()

                    def on_dst_delete():
                        def on_confirmation():
                            output_container.clear()

                            output_action_container.visible = True
                            output_action_container.update()

                        fkui.dialogs.show_confirm_dialog(
                            text=f"Are you sure you want to delete output destination '{dst_name}'?",
                            title="Delete Output",
                            on_confirmation=on_confirmation,
                            props="no-backdrop-dismiss"
                        )

                    with output_container:
                        with ui.element("div").style("margin-top:0.25rem;"):
                            with fk_card(dst_name, on_delete=on_dst_delete):
                                output_action_container.visible = False
                                output_action_container.update()

                                fk_destination.webui_info(*values)

                def show_destination_selector():
                    fkui.dialogs.show_fkio_selector(
                        "output",
                        fk_destinations,
                        on_select=create_destination_webui_config_info
                    )

                with ui.element("div").classes("w-full") as output_action_container:
                    ui.button(
                        text="Output",
                        on_click=show_destination_selector
                    ).style(
                        "min-height:48px;"
                        "width:100%;"
                    ).props("icon=output outline")

    return expansion


def _fk_separator(text: str):
    with ui.element("div").style(
            "display:flex;"
            "flex-flow:row nowrap;"
            "justify-content:center;"
            "align-items:center;"
            "position:relative;"
            "margin-bottom:1rem;"
    ):
        ui.label(text).style(
            "background:white;"
            "display:block;"
            "z-index:1;"
            "line-height:0.975rem;"
            "padding:0.12rem 0.24rem;"
            "font-weight:500;"
            "border-radius:0.2rem;"
            "border:1px solid var(--q-primary);"
            "color:var(--q-primary);"
        )

        ui.element("div").style(
            "width:100%;"
            "height:1px;"
            "background-color:var(--q-primary);"
            "position:absolute;"
        )


def fk_min_max_sliders(
        min_slider_label: str,
        max_slider_label: str,
        min: float,
        max: float,
        step: float,
        min_slider_value: float,
        max_slider_value: float
):
    with ui.grid(rows=2) as element:
        with ui.element("div").classes("w-full"):
            ui.label(min_slider_label)
            min_slider = ui.slider(
                min=min, max=max, step=step, value=min_slider_value
            ).props(f"label switch-label-side")

        with ui.element("div").classes("w-full"):
            ui.label(max_slider_label)
            max_slider = ui.slider(
                min=min, max=max, step=step, value=max_slider_value
            ).props(f"label inner-min=\"min\"")

        def update_min_slider(*args):
            max_value = max_slider.value

            min_slider._props["inner-max"] = max_value - step
            min_slider.update()

        def update_max_slider(*args):
            min_value = min_slider.value

            max_slider._props["inner-min"] = min_value + step
            max_slider.update()

        min_slider.on('change', update_max_slider)
        max_slider.on('change', update_min_slider)

        update_min_slider()
        update_max_slider()

        return min_slider, max_slider
