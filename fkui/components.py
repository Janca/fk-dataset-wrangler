from typing import Callable as _Callable

from nicegui import ui


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
