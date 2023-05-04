import os.path
from typing import Optional

from nicegui import ui

import fkui.components
import fkui.dialogs
import fkui.utils
import utils
from fkio.FkDestination import FkDestination
from fkio.FkSource import FkSource


class FkPipelineConfiguration:
    def __init__(self):
        self.fk_source: Optional[FkSource] = None
        self.fk_destination: Optional[FkDestination] = None
        pass


class FkWrangler:

    def __init__(self):
        _, task_classes = utils.load_modules_and_classes_from_directory(os.path.join("fktasks", "impl"), "fktasks.impl")
        src_classes, dst_classes = fkui.utils.load_fkio_classes()

        self.task_classes = task_classes
        self.src_classes = src_classes
        self.dst_classes = dst_classes

        self.pipeline_offset = 0
        self.pipeline_configs = {}

    def show(self):
        pipeline_container = ui.element("div").classes("w-full")
        pipeline_container_actions = ui.element("div").classes("w-full")

        with pipeline_container_actions:
            with ui.element("div").classes("w-full"):
                def on_click_new_pipeline():
                    pipeline_offset = self.pipeline_offset
                    self.pipeline_offset += 1

                    pipeline_config = FkPipelineConfiguration()
                    self.pipeline_configs[pipeline_offset] = pipeline_config

                    def on_pipeline_delete():
                        pipeline_container.remove(pipeline_expansion)
                        del self.pipeline_configs[pipeline_offset]

                    with pipeline_container:
                        pipeline_expansion = fkui.components.fk_pipeline(
                            pipeline_offset,
                            pipeline_config,
                            self.task_classes,
                            self.src_classes,
                            self.dst_classes,
                            on_delete=on_pipeline_delete
                        )

                        pipeline_expansion.open()

                def on_click_clear_pipelines():
                    def on_confirmation():
                        pipeline_container.clear()
                        self.pipeline_configs.clear()

                    fkui.dialogs.show_confirm_dialog(
                        text="Delete all pipelines? This action is irreversible.",
                        title="Delete Pipelines",
                        on_confirmation=on_confirmation
                    )

                with ui.row().style("justify-content:flex-end;"):
                    ui.button(
                        "New Pipeline",
                        on_click=on_click_new_pipeline
                    ).props("color=positive icon=queue").classes()

                    ui.button(
                        "Delete All",
                        on_click=on_click_clear_pipelines
                    ).props("color=negative outline icon=delete_sweep")

        ui.colors(primary="#3078fe")
        ui.run(title="FkDatasetWrangler", native=True, window_size=(468, 896))
