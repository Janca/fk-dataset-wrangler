import argparse
import json
import os
import sys
import time

import io
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
            tasks.FkTaskIntensiveness.LOW: 60,
            tasks.FkTaskIntensiveness.MEDIUM: 40,
            tasks.FkTaskIntensiveness.HIGH: 30,
            tasks.FkTaskIntensiveness.VERY_HIGH: 10,
            tasks.FkTaskIntensiveness.GPU: 1
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

    test_args = [
        "--output-image-ext", ".jpg",
        "--resource-usage", "make-my-pc-hurt",
        # "--require-caption-text",
        # "--required-tags", "scifi,futuristic,armour,armor,cyberpunk,punk,military,android,cybernetic,robot,"
        #                    "synthwave,fantasy,magic,spell,werewolf,mermaid,merman,zombie,wizard,witch,sorcerer,"
        #                    "cyberpunk,punk,car,tank,bomb,planet,space",
        # "--blacklisted-tags", "anime,1girl,1boy,waifu,senpai,drawing,painting,1woman,1man,chibi,sticker,"
        #                      "shrek,gigachad",
        # "--minimum-dimensions", "896x896",
        # "--normalize-captions",
        # "--brightness-min-threshold", "0.15",
        # "--brightness-max-threshold", "0.935",
        # "--square-ratio",
        # "--modes", "RGB",
        # "--scale", "896",
        # "--blur-threshold", "300",
        # "--entropy-threshold", "6.95",
        "--chad-score", "7.65",
        r"E:\MidJourney\2023_05_01",
        r"E:\MidJourney\2023_05_01_01"
    ]

    args = arg_parser.parse_args(args=(sys.argv[1:] or test_args or ['--help']))

    print("Pipeline arguments:")
    print(json.dumps(vars(args), sort_keys=True, indent=2))
    print()

    input_dirpath = args.src
    output_dirpath = args.dst
    image_ext = args.output_image_ext
    resource_pool_selection = args.resource_usage or "low"
    resource_pool = resource_pools[resource_pool_selection]
    gpu_multipass = False

    input_src = io.FkDirectorySource(input_dirpath, True)
    output_dst = io.FkDirectoryDestination(output_dirpath)

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

        buffer = io.FkPathBuffer()
        cpu_pipeline = tasks.FkPipeline(input_src, buffer, image_ext)
        for cpu_task in cpu_tasks:
            intensiveness = cpu_task.intensiveness
            max_workers = resource_pool[intensiveness]

            cpu_pipeline.add_task(cpu_task, max_workers)

        pipelines.append(cpu_pipeline)

        next_buffer = buffer
        for i, gpu_task in enumerate(gpu_tasks, start=1):
            out_buffer = io.FkPathBuffer() if i < len(gpu_tasks) else output_dst
            gpu_pipeline = tasks.FkPipeline(next_buffer, out_buffer, image_ext)

            intensiveness = gpu_task.intensiveness
            max_workers = resource_pool[intensiveness]

            gpu_pipeline.add_task(gpu_task, max_workers)
            next_buffer = out_buffer

            pipelines.append(gpu_pipeline)

        print(f"Completed multi-pass setup... {len(pipelines)} pipelines created...")

    else:
        pipeline = tasks.FkPipeline(input_src, output_dst, image_ext)
        for task in runtime_tasks:
            intensiveness = task.intensiveness
            max_workers = resource_pool[intensiveness]

            pipeline.add_task(task)

        pipelines.append(pipeline)

    for image_pipeline in pipelines:
        print("Setting up pipeline...")
        print()

        for pipeline_task in image_pipeline.tasks:
            print(f"Initializing task: {pipeline_task.__class__.__name__}")
            pipeline_task.initialize()

        print()

        try:
            print("Starting pipeline...")
            image_pipeline.start()

            print()
            print("Waiting for workers to complete...")
            while image_pipeline.active:
                time.sleep(1)

            print("Pipeline complete...")
            image_pipeline.shutdown()
            image_pipeline.report()

        except KeyboardInterrupt:
            print("Pipeline interrupted...")
            image_pipeline.report()
            sys.exit()

        print()
        print("-" * 42)
        print()
