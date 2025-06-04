import argparse as _argparse

import cv2 as _cv2
import nicegui.element
import numpy as _numpy
from nicegui import ui

import fkui.components
import utils
from fktasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage, \
    FkTaskIntensiveness as _FkTaskIntensiveness


class BlurFilter(_FkReportableTask):

    def __init__(self, blur_threshold: int = -1):
        self._blur_threshold = blur_threshold
        self._blur_scores: list[float] = []

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--blur-threshold",
            default=-1,
            type=float,
            help="discard image if image does not meet blur threshold "
                 "(0 - infinite; 0 = most blurry; default: -1 [disabled])"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        self._blur_threshold = args.blur_threshold
        return self._blur_threshold >= 0

    # noinspection PyUnresolvedReferences
    def process(self, image: _FkImage) -> bool:
        blur_score = _cv2.Laplacian(image.cv2_grayscale_image, _cv2.CV_64F).var()

        self._blur_scores.append(blur_score)
        return blur_score >= self._blur_threshold

    @property
    def priority(self) -> int:
        return 10_000

    @property
    def intensiveness(self) -> _FkTaskIntensiveness:
        return _FkTaskIntensiveness.HIGH

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self._blur_threshold),
            None,
            ("Average Blur", utils.safe_fn(lambda: _numpy.mean(self._blur_scores), -1)),
            ("90th Percentile", utils.safe_fn(lambda: _numpy.percentile(self._blur_scores, 90), -1))
        ]

    @classmethod
    def webui_config(cls, *args, **kwargs) -> tuple[nicegui.element.Element, list[nicegui.element.Element]]:
        with ui.element("div").classes("w-full") as element:
            ui.label("Blur Threshold")
            blur_threshold = ui.slider(
                min=0,
                max=10_000,
                value=350,
                step=1
            ).props("label")

        return element, [blur_threshold]

    @classmethod
    def webui_name(cls) -> str:
        return "Blur Filter"

    @classmethod
    def webui_validate(cls, *args, **kwargs) -> bool:
        # TODO: Implement actual validation logic
        return True

    @classmethod
    def webui_info(cls, *args, **kwargs):
        # TODO: Implement actual info display logic
        pass
