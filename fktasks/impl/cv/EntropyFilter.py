import argparse as _argparse

import cv2 as _cv2
import numpy as _numpy

import utils
from fktasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage, \
    FkTaskIntensiveness as _FkTaskIntensiveness


class EntropyFilter(_FkReportableTask):

    def __init__(self, entropy_threshold: float = -1):
        self._entropy_threshold = entropy_threshold
        self._entropy_scores = []

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--entropy-threshold",
            default=-1,
            type=float,
            help="discard image if image does not meet entropy threshold "
                 "(0 - 8; 0 = least entropic; 8 = most entropic; default: -1 [disabled])"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        self._entropy_threshold = args.entropy_threshold
        return self._entropy_threshold > 0

    # noinspection PyUnresolvedReferences
    def process(self, image: _FkImage) -> bool:
        grayscale_image = image.cv2_grayscale_image

        hist = _cv2.calcHist([grayscale_image], [0], None, [256], [0, 256])
        hist = hist.ravel() / hist.sum()
        logs = _numpy.nan_to_num(_numpy.log2(hist + _numpy.finfo(float).eps))
        entropy = -1 * (hist * logs).sum()

        del hist
        del logs

        self._entropy_scores.append(entropy)
        return entropy >= self._entropy_threshold

    @property
    def priority(self) -> int:
        return 10_100

    @property
    def intensiveness(self) -> _FkTaskIntensiveness:
        return _FkTaskIntensiveness.HIGH

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self._entropy_threshold),
            None,
            ("Average Entropy", utils.safe_fn(lambda: _numpy.mean(self._entropy_scores), -1)),
            ("90th Percentile", utils.safe_fn(lambda: _numpy.percentile(self._entropy_scores, 90), -1))
        ]
