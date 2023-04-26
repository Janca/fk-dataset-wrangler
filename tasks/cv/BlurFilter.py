import cv2 as _cv2
import numpy as _numpy

from tasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage


class BlurFilter(_FkReportableTask):

    def __init__(self, blur_threshold: int):
        self._blur_threshold = blur_threshold
        self._blur_scores: list[float] = []

    # noinspection PyUnresolvedReferences
    def process(self, image: _FkImage) -> bool:
        cv2_image = image.cv2_image

        grayscale_image = _cv2.cvtColor(cv2_image, _cv2.COLOR_BGR2GRAY)
        blur_score = _cv2.Laplacian(grayscale_image, _cv2.CV_64F).var()

        self._blur_scores.append(blur_score)
        return blur_score >= self._blur_threshold

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self._blur_threshold),
            None,
            ("Average Blur", _numpy.mean(self._blur_scores)),
            ("90th Percentile", _numpy.percentile(self._blur_scores, 90))
        ]
