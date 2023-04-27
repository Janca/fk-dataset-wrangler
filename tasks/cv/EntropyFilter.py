import cv2 as _cv2
import numpy as _numpy

from tasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage


class EntropyFilter(_FkReportableTask):

    def __init__(self, entropy_threshold: float):
        self._entropy_threshold = entropy_threshold
        self._entropy_scores = []

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

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self._entropy_threshold),
            None,
            ("Average Entropy", _numpy.mean(self._entropy_scores)),
            ("90th Percentile", _numpy.percentile(self._entropy_scores, 90))
        ]
