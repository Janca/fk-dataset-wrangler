import cv2 as _cv2

from tasks import FkTask as _FkTask, FkImage


class BlurFilter(_FkTask):

    def __init__(self, blur_threshold: int):
        self._blur_threshold = blur_threshold

    def process(self, image: FkImage) -> bool:
        cv2_image = image.cv2_image

        grayscale_image = _cv2.cvtColor(cv2_image, _cv2.COLOR_BGR2GRAY)
        blur_score = _cv2.Laplacian(grayscale_image, _cv2.CV_64F).var()

        return blur_score >= self._blur_threshold
