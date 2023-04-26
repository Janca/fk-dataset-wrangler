import os as _os
import queue as _queue
import time as _time
import traceback as _traceback
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor, Future as _Future
from threading import Thread as _Thread
from typing import Optional as _Optional

from tasks.FkTask import FkImage as _FkImage, FkTask as _FkTask, FkReportableTask as _FkExTask
from utils import KNOWN_IMAGE_EXTENSIONS as _KNOWN_IMAGE_EXTENSIONS, format_timestamp as _format_timestamp


class _FkTaskContext:
    def __init__(self, image: _FkImage):
        self._image = image
        self.attempts = 0

    @property
    def image(self):
        return self._image

    def destroy(self):
        self._image.destroy()

    def __del__(self):
        self.destroy()


class _FkTaskExecutor:
    def __init__(
            self, pipeline: "FkPipeline",
            task: _FkTask,
            max_workers: int = 10,
            max_attempts: int = 5
    ):
        self._max_attempts = max_attempts
        self._max_workers = max_workers

        self._pipeline = pipeline
        self._task = task

        self._queue: _queue.Queue[_FkTaskContext] = _queue.Queue()
        self._next_executor: _Optional[_FkTaskExecutor] = None

        self._processed_images = 0
        self._discarded_images = 0

        workers: list[_Thread] = []
        for _ in range(self._max_workers):
            worker_thread = _Thread(target=self._thread_fn, daemon=True)
            workers.append(worker_thread)
            worker_thread.start()

        self._workers = workers

    def submit(self, task: _FkTaskContext):
        self._queue.put(task, block=True)

    def _thread_fn(self):
        # noinspection PyProtectedMember
        while not self._pipeline._shutdown:
            try:
                task_context = self._queue.get(block=True, timeout=5)
                self._queue.task_done()

                if not task_context:
                    continue

                task_context.attempts += 1

                if task_context.attempts == 1:
                    self._processed_images += 1

                task_image = task_context.image

                # noinspection PyBroadException
                try:
                    task_successful = self._task.process(task_image)

                    if task_successful:
                        if self._next_executor:
                            task_context.attempts = 0
                            self._next_executor.submit(task_context)

                        else:  # no more executors; save image
                            try:
                                self._pipeline.save(task_context)
                            except:
                                pass

                    else:
                        if task_context.attempts == 1:
                            self._discarded_images += 1

                        task_context.destroy()

                        continue

                except Exception as e:
                    _traceback.print_exception(e)

                    # noinspection PyUnboundLocalVariable
                    attempts = task_context.attempts
                    if attempts > self._max_attempts:
                        task_context.destroy()
                        continue

                    self.submit(task_context)

            except _queue.Empty:
                continue


class FkPipeline:
    def __init__(
            self,
            input_dirpath: str,
            output_dirpath: str,
            image_ext: str = ".png",
            caption_text_ext: str = ".txt"
    ):
        self.input_dirpath = input_dirpath
        self.output_dirpath = output_dirpath

        self.image_ext = image_ext
        self.caption_text_ext = caption_text_ext

        self._executors: list[_FkTaskExecutor] = []

        self._save_futures: list[_Future] = []
        self._save_executor = _ThreadPoolExecutor(max_workers=1)

        self._started = False
        self._shutdown = False

        self._dry_run = False

        self._start_time = -1
        self._shutdown_time = -1

        self._processed_image_count = 0
        self._scanned_directory_count = 0
        self._images_saved_count = 0

    @property
    def active(self):
        if not self._started:
            raise RuntimeError("Pipeline is not started.")

        for save_future in self._save_futures:
            if not save_future.done():
                return True

        for executor in self._executors:
            # noinspection PyProtectedMember
            if not executor._queue.empty():
                return True

        return False

    def add_task(self, task: _FkTask, max_workers: int = 4, max_attempts: int = 5):
        if self._started:
            raise RuntimeError("Pipeline already started.")

        task_executor = _FkTaskExecutor(self, task, max_workers, max_attempts)
        self._executors.append(task_executor)

    def start(self, dry_run: bool = False):
        self._started = True
        self._dry_run = dry_run

        tasks_len = len(self._executors)
        for i in range(tasks_len - 1):
            # noinspection PyProtectedMember
            self._executors[i]._next_executor = self._executors[i + 1]

        print("Tasks:", tasks_len)
        entry_executor = self._executors[0]

        loaded_directories = 0
        loaded_images = 0

        def scan_dirpath(dirpath: str):
            nonlocal loaded_directories, loaded_images

            loaded_directories += 1
            for filename in _os.listdir(dirpath):
                filepath = _os.path.join(dirpath, filename)

                if _os.path.isdir(filepath):
                    scan_dirpath(filepath)

                else:
                    file_ext = _os.path.splitext(filename)[1]
                    if file_ext not in _KNOWN_IMAGE_EXTENSIONS:
                        continue

                    image = _FkImage(filepath)
                    task_context = _FkTaskContext(image)
                    entry_executor.submit(task_context)

                    loaded_images += 1

        _os.makedirs(self.output_dirpath, exist_ok=True)

        self._start_time = _time.time()

        print("Scanning directory:", self.input_dirpath)
        scan_dirpath(self.input_dirpath)

        self._processed_image_count = loaded_images
        self._scanned_directory_count = loaded_directories

        if loaded_images <= 0:
            self.shutdown()

    def report(self):
        print()

        for executor in self._executors:
            # noinspection PyProtectedMember
            executor_task = executor._task

            print(executor_task.name)
            print("-" * 42)

            # noinspection PyProtectedMember
            print(f"Processed Images: {executor._processed_images}")

            # noinspection PyProtectedMember
            print(f"Discarded Images: {executor._discarded_images}")

            if isinstance(executor_task, _FkExTask):
                print()

                report = executor_task.report()
                for report_item in report:
                    if not report_item:
                        print()

                    else:
                        description, value = report_item
                        if isinstance(value, float):
                            value = round(value, 3)

                        print(f"{description}: {value}")

            print()
            print()

        runtime_seconds = self._shutdown_time - self._start_time
        runtime_formatted = _format_timestamp(runtime_seconds)

        print("Pipeline Results")
        print("-" * 42)

        print(f"Directories scanned: {self._scanned_directory_count}")
        print(f"Image files processed: {self._processed_image_count}")
        print()

        discarded_image_count = self._processed_image_count - self._images_saved_count

        print(f"Images saved: {self._images_saved_count}")
        print(f"Discarded images: {discarded_image_count}")
        print()

        print(f"Completed in: {runtime_formatted}")

        print()

    def shutdown(self):
        self._shutdown = True
        self._shutdown_time = _time.time()

        self._save_executor.shutdown(wait=True, cancel_futures=True)

        self.report()

    def save(self, task_context: _FkTaskContext):
        if self._shutdown:
            raise RuntimeError("Pipeline shutdown.")

        if self._dry_run:
            self._images_saved_count += 1
            task_context.destroy()
            return

        # noinspection PyBroadException
        def save_fn():
            try:
                task_context.image.save(self.output_dirpath, self.image_ext, self.caption_text_ext)
                self._images_saved_count += 1
                task_context.destroy()

            except Exception as e:
                _traceback.print_exception(e)
                pass

        save_future = self._save_executor.submit(save_fn)
        self._save_futures.append(save_future)
