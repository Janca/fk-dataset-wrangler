import argparse as _argparse

import utils
from fktasks import FkTask as _FkTask, FkImage as _FkImage, FkTaskIntensiveness as _FkTaskIntensiveness


class ImageScaler(_FkTask):
    def __init__(self, max_size: int = -1):
        self._max_size = max_size

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--scale",
            default=-1,
            type=int,
            help="scale image to the provided size, keeping aspect ratio "
                 "(default: -1 [disabled])"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        self._max_size = args.scale
        return self._max_size > 0

    def process(self, image: _FkImage) -> bool:
        image.image = utils.resize_image_aspect(image.image, self._max_size)
        return True

    @property
    def priority(self) -> int:
        return 600

    @property
    def intensiveness(self) -> _FkTaskIntensiveness:
        return _FkTaskIntensiveness.LOW

    @classmethod
    def webui_config(cls, *args, **kwargs):
        # TODO: Implement actual config UI
        pass

    @classmethod
    def webui_validate(cls, *args, **kwargs) -> bool:
        # TODO: Implement actual validation logic
        return True

    @classmethod
    def webui_info(cls, *args, **kwargs):
        # TODO: Implement actual info display logic
        pass
