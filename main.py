import argparse
import json
import os
import sys
import time

import tasks
import utils

if __name__ == '__main__':
    resource_pools = {
        "low": {
            tasks.FkTaskIntensiveness.LOW: 5,
            tasks.FkTaskIntensiveness.MEDIUM: 5,
            tasks.FkTaskIntensiveness.HIGH: 2,
            tasks.FkTaskIntensiveness.VERY_HIGH: 1,
            tasks.FkTaskIntensiveness.GPU: 1
        },
        "med": {
            tasks.FkTaskIntensiveness.LOW: 10,
            tasks.FkTaskIntensiveness.MEDIUM: 10,
            tasks.FkTaskIntensiveness.HIGH: 5,
            tasks.FkTaskIntensiveness.VERY_HIGH: 2,
            tasks.FkTaskIntensiveness.GPU: 1
        },
        "high": {
            tasks.FkTaskIntensiveness.LOW: 30,
            tasks.FkTaskIntensiveness.MEDIUM: 20,
            tasks.FkTaskIntensiveness.HIGH: 10,
            tasks.FkTaskIntensiveness.VERY_HIGH: 5,
            tasks.FkTaskIntensiveness.GPU: 1
        },
        "make-my-pc-hurt": {
            tasks.FkTaskIntensiveness.LOW: 40,
            tasks.FkTaskIntensiveness.MEDIUM: 30,
            tasks.FkTaskIntensiveness.HIGH: 20,
            tasks.FkTaskIntensiveness.VERY_HIGH: 5,
            tasks.FkTaskIntensiveness.GPU: 2
        }
    }

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

    arg_parser.add_argument(
        "--resource-usage",
        default="low",
        choices=list(resource_pools.keys()),
        help="configure pipeline to use more or less resources (default: low)"
    )

    working_directory = os.path.dirname(os.path.realpath(__file__))
    tasks_directory = os.path.join(working_directory, "tasks", "impl")
    _, tasks_classes = utils.load_modules_and_classes_from_directory(tasks_directory)

    tasks_instances = [task_class() for task_class in tasks_classes if not task_class.__name__.startswith("_")]
    for task_inst in tasks_instances:
        task_group = arg_parser.add_argument_group(f"{task_inst.__class__.__name__} options")
        task_inst.register_args(task_group)

    test_args = None

    args = arg_parser.parse_args(args=(test_args or sys.argv[1:] or ['--help']))

    print("Pipeline arguments:")
    print(json.dumps(vars(args), sort_keys=True, indent=2))
    print()

    input_dirpath = args.src
    output_dirpath = args.dst
    image_ext = args.output_image_ext
    resource_pool_selection = args.resource_usage or "low"
    resource_pool = resource_pools[resource_pool_selection]
    gpu_multipass = True

    input_src = tasks.FkDirectorySource(input_dirpath, True)
    output_dst = tasks.FkDirectoryDestination(output_dirpath)

    runtime_tasks: list[tasks.FkTask] = []
    for task_inst in tasks_instances:
        if task_inst.parse_args(args):
            runtime_tasks.append(task_inst)

    runtime_tasks = sorted(runtime_tasks, key=lambda task: task.priority)
    pipelines: list[tasks.FkPipeline] = []

    if gpu_multipass:
        cpu_tasks = []
        gpu_tasks = []

        for task in runtime_tasks:
            if task.intensiveness == tasks.FkTaskIntensiveness.GPU:
                gpu_tasks.append(task)

            else:
                cpu_tasks.append(task)

        buffer = tasks.FkBuffer()
        cpu_pipeline = tasks.FkPipeline(input_src, buffer, image_ext)
        for cpu_task in cpu_tasks:
            cpu_pipeline.add_task(cpu_task)

        pipelines.append(cpu_pipeline)

        next_buffer = buffer
        for i, gpu_task in enumerate(gpu_tasks, start=1):
            out_buffer = tasks.FkBuffer() if i < len(gpu_tasks) else output_dst
            gpu_pipeline = tasks.FkPipeline(next_buffer, out_buffer, image_ext)
            gpu_pipeline.add_task(gpu_task)

            next_buffer = out_buffer
            pipelines.append(gpu_pipeline)

        print(f"Completed multi-pass setup... {len(pipelines)} pipelines created...")

    else:
        pipeline = tasks.FkPipeline(input_src, output_dst, image_ext)
        pipelines.append(pipeline)

    for image_pipeline in pipelines:
        print("Setting up pipeline...")
        print()

        for pipeline_task in image_pipeline.tasks:
            print(f"Initializing task: {pipeline_task.__class__.__name__}")
            pipeline_task.initialize()

            intensiveness = pipeline_task.intensiveness
            max_workers = resource_pool[intensiveness]

            image_pipeline.add_task(pipeline_task, max_workers=max_workers)

        print()

        print("Starting pipeline...")
        image_pipeline.start()

        try:
            print()
            print("Waiting for workers to complete...")
            while image_pipeline.active:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Pipeline interrupted...")
            image_pipeline.shutdown()
            image_pipeline.report()
            sys.exit()

        print("Pipeline complete...")
        image_pipeline.shutdown()
        image_pipeline.report()

        print()
        print("-" * 42)
        print()
