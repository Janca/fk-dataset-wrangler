import argparse as _argparse

import cv2 as _cv2
import numpy as _numpy

import utils
from tasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage


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
        return 600

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self._blur_threshold),
            None,
            ("Average Blur", utils.safe_fn(lambda: _numpy.mean(self._blur_scores), -1)),
            ("90th Percentile", utils.safe_fn(lambda: _numpy.percentile(self._blur_scores, 90), -1))
        ]
