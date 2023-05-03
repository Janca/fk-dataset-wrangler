from nicegui import ui

import fkui.components
import fkui.dialogs
import fkui.utils
from fkio.FkSource import FkSource as _FkSource


class FkWrangler:

    def __init__(self):
        self.pipelines = []
        self.available_sources = []

        src_classes, dst_classes = fkui.utils.load_fkio_classes()

        self.src_classes = src_classes
        self.dst_classes = dst_classes

    def show(self):
        pipeline_container = ui.element("div").classes("w-full")
        pipeline_container_actions = ui.element("div").classes("w-full")

        with pipeline_container_actions:
            with ui.element("div"):
                def on_click_new_pipeline():
                    with pipeline_container:
                        pipeline_expansion = self.create_pipeline()
                        pipeline_expansion.open()

                def on_click_clear_pipelines():
                    for pipeline in self.pipelines:
                        pipeline_container.remove(pipeline)

                    self.pipelines.clear()

                with ui.row().style("justify-content:flex-end;"):
                    ui.button(
                        "New Pipeline",
                        on_click=on_click_new_pipeline
                    ).props("color=positive icon=queue").classes()

                    ui.button(
                        "Delete All Pipeline",
                        on_click=on_click_clear_pipelines
                    ).props("color=negative outline icon=delete_sweep")

        ui.colors(primary="#3078fe")
        ui.run(title="FkDatasetWrangler", native=True)

    def create_pipeline(self):
        pipeline_id = len(self.pipelines) + 1

        with ui.expansion(
                f"Pipeline #{pipeline_id}",
                icon="filter_alt"
        ).props(
            "group=pipeline expand-icon-toggle"
        ).props(
            "header-style=font-weight:500"
        ).classes("w-full") as pipeline_expansion:
            with pipeline_expansion.add_slot("header"):
                with ui.row().style(
                        "min-height:100%;"
                        "width:100%;"
                        "justify-content:flex-start;"
                        "align-items:center"
                ):
                    with ui.element("div").style(
                            "display:flex;"
                            "width:100%;"
                            "flex-flow:row nowrap;"
                    ):
                        ui.icon("filter_list").style("font-size:1.48rem;margin-right:0.4rem;")
                        ui.label(f"Pipeline #{pipeline_id}").style("font-size:1rem;font-weight:500;")
                        ui.button().props(
                            "icon=delete "
                            "flat "
                            "color=negative "
                            "size=sm "
                            "dense "
                            ""
                        ).style("justify-self:flex-end;margin-left:auto;margin-right:0.2rem;")

            with ui.element("div"):
                with ui.grid(rows=3).style("padding:1rem 0; gap:1rem;grid-template-rows:auto 1fr;"):
                    with ui.element("div"):
                        with ui.element("div") as input_container:
                            pass

                        def create_input_info(src_cls: _FkSource, values):
                            with input_container:
                                with ui.element("div"):
                                    input_name = src_cls.friendly_name()

                                    def delete_input():
                                        input_container.clear()

                                        input_actions.visible = True
                                        input_actions.update()

                                    with fkui.components.fk_card(input_name, on_delete=delete_input):
                                        input_info = src_cls.webui_pipeline_info(*values)

                                    input_actions.visible = False
                                    input_actions.update()

                        with ui.element("div") as input_actions:
                            ui.button(
                                "Input",
                                on_click=lambda: fkui.dialogs.show_source_selector(
                                    self.src_classes,
                                    lambda src, v: create_input_info(src, v)
                                )
                            ).style(
                                "min-height:48px"
                            ).props("icon=input outline").classes("w-full")

                    with ui.element("div"):
                        with ui.element("div") as task_container:
                            pass

                        with ui.element("div") as task_actions:
                            ui.button("Add Task").style(
                                "min-height:48px"
                            ).props("icon=add_task outline").classes("w-full")

                    with ui.element("div"):
                        with ui.element("div") as output_container:
                            pass

                        with ui.element("div") as output_actions:
                            ui.button("Output").style(
                                "min-height:48px"
                            ).props("icon=output outline").classes("w-full")

        self.pipelines.append(pipeline_expansion)
        return pipeline_expansion
