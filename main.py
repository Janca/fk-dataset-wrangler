import argparse
import os
import sys
import time

import tasks
import utils

_TASK_POOL_SIZES = {
    "low": (10, 5, 1, 1),
    "med": (20, 10, 5, 1),
    "high": (30, 15, 10, 1),
    "make-my-pc-hurt": (60, 40, 20, 2)
}

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "src",
        help="dataset input folder"
    )

    arg_parser.add_argument(
        "dst",
        help="dataset output folder"
    )

    arg_parser.add_argument(
        "--output-image-ext",
        default=".png",
        help="extension to use when saving images to the dataset output folder "
             "(default: .png)"
    )

    arg_parser.add_argument(
        "--output-caption-text-ext",
        default=".txt",
        help="extension to use when saving image caption text to the dataset output folder "
             "(default: .txt)"
    )

    working_directory = os.path.dirname(os.path.realpath(__file__))
    tasks_directory = os.path.join(working_directory, "tasks", "impl")
    _, tasks_classes = utils.load_modules_and_classes_from_directory(tasks_directory)

    tasks_instances = [task_class() for task_class in tasks_classes if not task_class.__name__.startswith("_")]
    for task_inst in tasks_instances:
        task_group = arg_parser.add_argument_group(f"{task_inst.__class__.__name__} options")
        task_inst.register_args(task_group)

    args = arg_parser.parse_args(args=(sys.argv[1:] or ['--help']))

    input_dirpath = args.src
    output_dirpath = args.dst
    image_ext = args.output_image_ext

    runtime_tasks = []
    for task_inst in tasks_instances:
        if task_inst.parse_args(args):
            runtime_tasks.append(task_inst)

    runtime_tasks = sorted(runtime_tasks, key=lambda task: task.priority)

    image_pipeline = tasks.FkPipeline(
        input_dirpath,
        output_dirpath,
        image_ext=image_ext
    )

    print("Setting up pipeline...")
    print()

    for runtime_task in runtime_tasks:
        print(f"Adding task: {runtime_task.__class__.__name__}")
        image_pipeline.add_task(runtime_task)

    print()

    print("Starting pipeline...")
    image_pipeline.start()

    try:
        print()
        print("Waiting for workers to complete...")
        while image_pipeline.active:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Pipeline interrupted.")
        image_pipeline.shutdown()
        sys.exit()

    print("Shutting down pipeline...")
    image_pipeline.shutdown()
