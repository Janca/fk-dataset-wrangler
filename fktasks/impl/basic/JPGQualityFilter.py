import argparse as _argparse

import nicegui.element
import numpy as _numpy
from PIL.Image import Image as _PillowImage
from PIL.JpegImagePlugin import JpegImageFile as _PillowJPG
from nicegui import ui

import utils
from fktasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage, \
    FkTaskIntensiveness as _FkTaskIntensiveness


class JPGQualityFilter(_FkReportableTask):
    _NUM_QUANT_TBLS = 4
    _DCTSIZE2 = 64

    _HASH_2 = [
        1020, 1015, 932, 848, 780, 735, 702, 679, 660, 645,
        632, 623, 613, 607, 600, 594, 589, 585, 581, 571,
        555, 542, 529, 514, 494, 474, 457, 439, 424, 410,
        397, 386, 373, 364, 351, 341, 334, 324, 317, 309,
        299, 294, 287, 279, 274, 267, 262, 257, 251, 247,
        243, 237, 232, 227, 222, 217, 213, 207, 202, 198,
        192, 188, 183, 177, 173, 168, 163, 157, 153, 148,
        143, 139, 132, 128, 125, 119, 115, 108, 104, 99,
        94, 90, 84, 79, 74, 70, 64, 59, 55, 49,
        45, 40, 34, 30, 25, 20, 15, 11, 6, 4,
        0
    ]

    _SUMS_2 = [
        32640, 32635, 32266, 31495, 30665, 29804, 29146, 28599, 28104,
        27670, 27225, 26725, 26210, 25716, 25240, 24789, 24373, 23946,
        23572, 22846, 21801, 20842, 19949, 19121, 18386, 17651, 16998,
        16349, 15800, 15247, 14783, 14321, 13859, 13535, 13081, 12702,
        12423, 12056, 11779, 11513, 11135, 10955, 10676, 10392, 10208,
        9928, 9747, 9564, 9369, 9193, 9017, 8822, 8639, 8458,
        8270, 8084, 7896, 7710, 7527, 7347, 7156, 6977, 6788,
        6607, 6422, 6236, 6054, 5867, 5684, 5495, 5305, 5128,
        4945, 4751, 4638, 4442, 4248, 4065, 3888, 3698, 3509,
        3326, 3139, 2957, 2775, 2586, 2405, 2216, 2037, 1846,
        1666, 1483, 1297, 1109, 927, 735, 554, 375, 201,
        128, 0
    ]
    _HASH_1 = [
        510, 505, 422, 380, 355, 338, 326, 318, 311, 305,
        300, 297, 293, 291, 288, 286, 284, 283, 281, 280,
        279, 278, 277, 273, 262, 251, 243, 233, 225, 218,
        211, 205, 198, 193, 186, 181, 177, 172, 168, 164,
        158, 156, 152, 148, 145, 142, 139, 136, 133, 131,
        129, 126, 123, 120, 118, 115, 113, 110, 107, 105,
        102, 100, 97, 94, 92, 89, 87, 83, 81, 79,
        76, 74, 70, 68, 66, 63, 61, 57, 55, 52,
        50, 48, 44, 42, 39, 37, 34, 31, 29, 26,
        24, 21, 18, 16, 13, 11, 8, 6, 3, 2,
        0
    ]
    _SUMS_1 = [
        16320, 16315, 15946, 15277, 14655, 14073, 13623, 13230, 12859,
        12560, 12240, 11861, 11456, 11081, 10714, 10360, 10027, 9679,
        9368, 9056, 8680, 8331, 7995, 7668, 7376, 7084, 6823,
        6562, 6345, 6125, 5939, 5756, 5571, 5421, 5240, 5086,
        4976, 4829, 4719, 4616, 4463, 4393, 4280, 4166, 4092,
        3980, 3909, 3835, 3755, 3688, 3621, 3541, 3467, 3396,
        3323, 3247, 3170, 3096, 3021, 2952, 2874, 2804, 2727,
        2657, 2583, 2509, 2437, 2362, 2290, 2211, 2136, 2068,
        1996, 1915, 1858, 1773, 1692, 1620, 1552, 1477, 1398,
        1326, 1251, 1179, 1109, 1031, 961, 884, 814, 736,
        667, 592, 518, 441, 369, 292, 221, 151, 86,
        64, 0
    ]

    def __init__(self, jpg_quality_threshold: int = -1):
        self._jpg_quality_threshold = jpg_quality_threshold
        self._qualities = []

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--jpeg-quality",
            default=-1,
            type=int,
            help="discard images if they are not at least the provided quality level "
                 "(0 - 100; default: -1 [disabled])"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        self._jpg_quality_threshold = args.jpeg_quality
        return self._jpg_quality_threshold >= 0

    def process(self, image: _FkImage) -> bool:
        if isinstance(image.image, _PillowJPG):
            # apparently image extensions don't mean shit, PIL will
            # open w.e even named wrong, so check instance type instead

            jpeg_quality = JPGQualityFilter._get_jpg_quality(image.image)
            if jpeg_quality >= 0:
                self._qualities.append(jpeg_quality)
                return jpeg_quality >= self._jpg_quality_threshold

            return True  # unknown quality

        else:
            return True

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self._jpg_quality_threshold),
            None,
            ("Average Quality", utils.safe_fn(lambda: int(_numpy.mean(self._qualities)), -1)),
            ("90th Percentile", utils.safe_fn(lambda: _numpy.percentile(self._qualities, 90), -1))
        ]

    @property
    def priority(self) -> int:
        return 300

    @property
    def intensiveness(self) -> _FkTaskIntensiveness:
        return _FkTaskIntensiveness.MEDIUM

    @classmethod
    def webui_config(cls, *args, **kwargs) -> tuple[nicegui.element.Element, list[nicegui.element.Element]]:
        with ui.element("div") as element:
            ui.label("JPG Quality")
            jpg_slider = ui.slider(min=1, max=100, step=1, value=75).props("label")

        return element, [jpg_slider]

    @classmethod
    def webui_name(cls) -> str:
        return "JPG Quality Filter"

    @classmethod
    def webui_validate(cls, *args, **kwargs) -> bool:
        # TODO: Implement actual validation logic
        return True

    @classmethod
    def webui_info(cls, *args, **kwargs):
        # TODO: Implement actual info display logic
        pass

    @classmethod
    def _get_jpg_quality(cls, image: _PillowImage) -> int:
        """
        Stolen from gist
        https://gist.github.com/eddy-geek/c0f01dc5401dc50a49a0a821cdc9b3e8#file-jpg_quality_pil_magick-py

        Implement quality computation following ImageMagick heuristic algorithm:
        https://github.com/ImageMagick/ImageMagick/blob/7.1.0-57/coders/jpeg.c#L782
        Usage:
        ```
        pim = Img.open(...)
        quality = get_jpg_quality(pim)
        ```
        See also https://stackoverflow.com/questions/4354543/
        """

        qsum = 0

        # noinspection PyBroadException
        try:
            # noinspection PyUnresolvedReferences
            qdict = image.quantization
        except Exception:
            return -2

        for i, qtable in qdict.items():
            qsum += sum(qtable)

        if len(qdict) >= 1:
            qvalue = qdict[0][2] + qdict[0][53]
            hash, sums = JPGQualityFilter._HASH_1, JPGQualityFilter._SUMS_1

            if len(qdict) >= 2:
                qvalue += qdict[1][0] + qdict[1][-1]
                hash, sums = JPGQualityFilter._HASH_2, JPGQualityFilter._SUMS_2

            for i in range(100):
                if (qvalue < hash[i]) and (qsum < sums[i]):
                    continue

                if ((qvalue <= hash[i]) and (qsum <= sums[i])) or (i >= 50):
                    return i + 1

                break

        return -1
