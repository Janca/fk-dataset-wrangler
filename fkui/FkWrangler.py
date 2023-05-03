from nicegui import ui

import fkui.components
import fkui.dialogs
import fkui.utils


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
                        pipeline_expansion = fkui.components.fk_pipeline(0, self.src_classes)
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
        ui.run(title="FkDatasetWrangler")
