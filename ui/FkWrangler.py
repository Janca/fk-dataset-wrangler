import inspect
import os.path

from nicegui import ui

import tasks.io
import utils


class FkWrangler:

    def __init__(self):
        self.pipelines = []
        self.available_sources = []

        print("Printing")
        self.load_sources()

    def load_sources(self):
        source_class_package = os.path.join("tasks", "io")
        _, source_classes = utils.load_modules_and_classes_from_directory(source_class_package)

        source_classes = [cls for cls in source_classes if inspect.isclass(cls)]
        for cls in source_classes:
            print(cls)

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

                with ui.row().style("justify-content:flex-end"):
                    ui.button(
                        "New Pipeline",
                        on_click=on_click_new_pipeline
                    ).props("color=positive icon=queue").classes()

                    ui.button(
                        "Clear Pipeline",
                        on_click=on_click_clear_pipelines
                    ).props("color=negative outline icon=delete_sweep")

        ui.run(title="FkDatasetWrangler")

    def create_pipeline(self):
        pipeline_id = len(self.pipelines) + 1

        with ui.expansion(
                f"Pipeline #{pipeline_id}",
                icon="filter_alt"
        ).props("group=pipeline header-style=font-size:1rem").classes("w-full") as pipeline_expansion:
            with ui.element("div"):
                pipeline_task_container = ui.element("div")
                self.load_sources()

                with ui.grid(rows=3).style("padding:0.6rem 0; gap:0.4rem"):
                    with ui.element("div"):
                        with ui.element("div") as input_container:
                            pass

                        with ui.element("div") as input_actions:
                            ui.button("Input").props("icon=input color=text outline").classes("w-full")

                    with ui.element("div"):
                        with ui.element("div") as task_container:
                            pass

                        with ui.element("div") as task_actions:
                            ui.button("Add Task").props("icon=add_task color=text outline").classes("w-full")

                    with ui.element("div"):
                        with ui.element("div") as output_container:
                            pass

                        with ui.element("div") as output_actions:
                            ui.button("Output").props("icon=output color=text outline").classes("w-full")

        self.pipelines.append(pipeline_expansion)
        return pipeline_expansion
