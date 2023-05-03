import argparse as _argparse
import math as _math

import PIL.ImageStat as _PILImageStat
import numpy as _numpy

import utils
from fktasks import FkImage as _FkImage, FkTaskIntensiveness as _FkTaskIntensiveness
from fktasks.FkTask import FkReportableTask as _FkReportableTask


class BrightnessFilter(_FkReportableTask):

    def __init__(self, min_brightness_threshold: float = -1, max_brightness_threshold: float = -1):
        self._min_brightness_threshold = min_brightness_threshold
        self._max_brightness_threshold = max_brightness_threshold
        self._brightnesses = []

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--brightness-min-threshold",
            default=-1,
            type=float,
            help="discard image under brightness threshold (0.0 - 1.0; "
                 "0 = most dark; "
                 "1 = most bright; "
                 "default = -1 [disabled])"
        )

        arg_parser.add_argument(
            "--brightness-max-threshold",
            default=-1,
            type=float,
            help="discard image over brightness threshold (0.0 - 1.0; "
                 "0 = most dark; "
                 "1 = most bright; "
                 "default: -1 [disabled])"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        self._min_brightness_threshold = args.brightness_min_threshold
        self._max_brightness_threshold = args.brightness_max_threshold

        return 0 < self._min_brightness_threshold < self._max_brightness_threshold and self._max_brightness_threshold > 0

    def process(self, image: _FkImage) -> bool:
        temp_image = image.image.convert("RGB")
        image_stat = _PILImageStat.Stat(temp_image)

        r, g, b = image_stat.mean

        perceived_brightness = _math.sqrt((0.241 * (r ** 2)) + (0.691 * (g ** 2)) + (0.068 * (b ** 2))) / 255
        temp_image.close()

        self._brightnesses.append(perceived_brightness)

        if 0 < self._min_brightness_threshold > perceived_brightness:
            return False

        if 0 < self._max_brightness_threshold < perceived_brightness:
            return False

        return True

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Minimum Threshold", self._min_brightness_threshold),
            ("Filter Maximum Threshold", self._max_brightness_threshold),
            None,
            ("Average Brightness", utils.safe_fn(lambda: _numpy.mean(self._brightnesses), -1)),
            ("90th Percentile", utils.safe_fn(lambda: _numpy.percentile(self._brightnesses, 90), -1))
        ]

    @property
    def priority(self) -> int:
        return 400

    @property
    def intensiveness(self) -> _FkTaskIntensiveness:
        return _FkTaskIntensiveness.LOW


