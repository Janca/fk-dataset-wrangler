import cv2 as _cv2
import numpy as _numpy

import utils
from tasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage


class BlurFilter(_FkReportableTask):

    def __init__(self, blur_threshold: int):
        self._blur_threshold = blur_threshold
        self._blur_scores: list[float] = []

    # noinspection PyUnresolvedReferences
    def process(self, image: _FkImage) -> bool:
        blur_score = _cv2.Laplacian(image.cv2_grayscale_image, _cv2.CV_64F).var()

        self._blur_scores.append(blur_score)
        return blur_score >= self._blur_threshold

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self._blur_threshold),
            None,
            ("Average Blur", utils.safe_fn(lambda: _numpy.mean(self._blur_scores), -1)),
            ("90th Percentile", utils.safe_fn(lambda: _numpy.percentile(self._blur_scores, 90), -1))
        ]
