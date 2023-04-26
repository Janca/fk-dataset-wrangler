import hashlib as _hashlib
import os as _os
import queue as _queue
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor, Future as _Future
from threading import Thread as _Thread
from typing import Optional as _Optional

from tasks.FkTask import FkImage as _FkImage, FkTask as _FkTask
from utils import KNOWN_IMAGE_EXTENSIONS as _KNOWN_IMAGE_EXTENSIONS


class _FkAltTaskContext:
    def __init__(self, image: _FkImage):
        self._image = image
        self.attempts = 0

    @property
    def image(self):
        return self._image


class _FkAltExecutor:
    def __init__(
            self, pipeline: "FkPipeline",
            task: _FkTask,
            queue_depth: int = -1,
            max_workers: int = 10,
            max_attempts: int = 5
    ):
        self._max_attempts = max_attempts
        self._max_workers = max_workers

        self._pipeline = pipeline
        self._task = task

        self._queue: _queue.Queue[_FkAltTaskContext] = _queue.Queue(maxsize=queue_depth)
        self._next_executor: _Optional[_FkAltExecutor] = None

        workers: list[_Thread] = []
        for _ in range(self._max_workers):
            worker_thread = _Thread(target=self._thread_fn, daemon=True)
            workers.append(worker_thread)
            worker_thread.start()

        self._workers = workers

    def submit(self, task: _FkAltTaskContext):
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
                task_image = task_context.image

                # noinspection PyBroadException
                try:
                    task_successful = self._task.process(task_image)

                    if task_successful:
                        if self._next_executor:
                            next_task_context = _FkAltTaskContext(task_image)
                            self._next_executor.submit(next_task_context)

                        else:  # no more executors; save image
                            try:
                                self._pipeline.save(task_image)

                            except:
                                pass

                    else:
                        task_image.close()
                        continue

                except Exception:
                    attempts = task_context.attempts
                    if attempts > self._max_attempts:
                        task_image.close()
                        continue

                    self.submit(task_context)

            except _queue.Empty:
                continue


class _FkTaskExecutor:
    def __init__(self, pipeline: "FkPipeline", task: _FkTask, max_workers: int = 10, max_attempts: int = 5):
        self.max_attempts = max_attempts

        self._pipeline = pipeline
        self._task = task
        self._tpe = _ThreadPoolExecutor(max_workers)

        self._next_executor: _Optional[_FkTaskExecutor] = None
        self._futures: list[_Future] = []

    def submit(self, image: _FkImage):
        # noinspection PyProtectedMember
        if self._pipeline._shutdown:
            raise RuntimeError("Pipeline is shutdown.")

        task_future = self._tpe.submit(lambda img=image: self._worker_fn(img))
        self._futures.append(task_future)

    def _worker_fn(self, image: _FkImage):
        task_attempt = 0
        task_successful = False

        # noinspection PyProtectedMember
        while not task_successful and task_attempt < self.max_attempts and not self._pipeline._shutdown:
            try:
                task_successful = self._task.process(image)
                if task_successful:
                    if self._next_executor:  # submit image result to next executor
                        self._next_executor.submit(image)

                    else:  # next executor is none; save image
                        try:
                            self._pipeline.save(image)
                        except Exception as e:
                            image.close()

                else:  # task was not successful; close image
                    image.close()
                    break

            except KeyboardInterrupt:
                break

            except Exception as e:
                task_attempt += 1
                if task_attempt >= self.max_attempts:
                    break

    @property
    def futures(self):
        return self._futures


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

        self._executors: list[_FkAltExecutor] = []

        self._save_futures: list[_Future] = []
        self._save_executor = _ThreadPoolExecutor(max_workers=1)

        self._started = False
        self._shutdown = False

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

            # for future in executor.futures:
            #     if not future.done():
            #         return True

        return False

    def add_task(self, task: _FkTask, max_workers: int = 4, max_attempts: int = 5):
        if self._started:
            raise RuntimeError("Pipeline already started.")

        task_executor = _FkAltExecutor(self, task, max_workers, max_attempts)
        self._executors.append(task_executor)

    def start(self):
        self._started = True

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
                    task_context = _FkAltTaskContext(image)
                    entry_executor.submit(task_context)

                    loaded_images += 1

        _os.makedirs(self.output_dirpath, exist_ok=True)

        scan_dirpath(self.input_dirpath)

        print("Scanned", loaded_directories, "directories...")
        print("Scanned", loaded_images, "images...")

    def shutdown(self):
        self._shutdown = True
        self._save_executor.shutdown(wait=True, cancel_futures=True)

        # for executor in self._executors:
        #     # noinspection PyProtectedMember
        #     executor._tpe.shutdown(wait=True, cancel_futures=True)

    def save(self, image: _FkImage):
        if self._shutdown:
            raise RuntimeError("Pipeline shutdown.")

        save_future = self._save_executor.submit(lambda img=image: self._save_image(img))
        self._save_futures.append(save_future)

    def _save_image(self, image: _FkImage):
        filename_hash = _hashlib.sha256(image.basename.encode("utf-8")).hexdigest()

        save_image_filepath = _os.path.join(
            self.output_dirpath,
            filename_hash + self.image_ext
        )

        image.image.save(save_image_filepath, quality=95 if self.image_ext in [".jpg", ".jpeg"] else None)
        image.close()

        if image.caption_text:
            save_caption_text_filepath = _os.path.join(
                self.output_dirpath,
                filename_hash + self.caption_text_ext
            )

            with open(
                    save_caption_text_filepath,
                    "w+",
                    encoding="utf-8",
                    errors="ignore"
            ) as caption_file:
                caption_file.write(image.caption_text)
