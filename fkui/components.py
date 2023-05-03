from typing import Callable as _Callable, Callable

from nicegui import ui

import fkui.dialogs
from fkio.FkSource import FkSource as _FkSource


def fk_card(title: str, on_delete: _Callable[[...], None] = None):
    with ui.element("div").style("position:relative;min-height:64px"):
        ui.badge(title).style(
            "z-index:100;"
            "font-size:0.75rem;"
            "font-weight:500;"
            "left:0.5rem;"
            "top:-0.5rem"
        ).classes("absolute p-1")

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

        return ui.card()


def fk_pipeline(
        index: int,
        fk_sources: list[_FkSource],
        name: str = None,
        on_delete: Callable[[], None] = None
):
    name = f"Pipeline #{index + 1}" if name is None else name
    with ui.expansion().props(
            "group=pipeline expand-icon-toggle"
    ).classes("w-full") as expansion:
        with expansion.add_slot("header"):
            with ui.row().style("min-height:100%;width:100%;align-items:center;"):
                ui.icon("filter_list").style("font-size:1.48rem;margin-right:0.4rem;")
                ui.label(name).style("font-size:1rem;font-weight:500;")
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
                ).style("justify-self:flex-end;margin-left:auto;margin-right:0.2rem;")

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
                    fkui.dialogs.show_source_selector(fk_sources, on_select=create_source_webui_config_info)

                with ui.element("div").classes("w-full") as source_action_container:
                    ui.button(
                        text="Input",
                        on_click=show_source_selector
                    ).style(
                        "min-height:48px;"
                        "width:100%;"
                    ).props("icon=input outline")

            with ui.element("div"):
                with ui.element("div").classes("w-full") as task_container:
                    pass

                with ui.element("div").classes("w-full") as task_action_container:
                    ui.button(
                        text="Add Task",
                    ).style(
                        "min-height:48px;"
                        "width:100%;"
                    ).props("icon=add_task outline")

            with ui.element("div"):
                with ui.element("div").classes("w-full") as output_container:
                    pass

                with ui.element("div").classes("w-full") as output_action_container:
                    ui.button(
                        text="Output",
                    ).style(
                        "min-height:48px;"
                        "width:100%;"
                    ).props("icon=output outline")

    return expansion
