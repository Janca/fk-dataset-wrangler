import argparse as _argparse

import imagehash as _imagehash

from fktasks import FkImage as _FkImage
from fktasks.FkTask import FkTask as _FkTask


class ImagePerceptualHashFilter(_FkTask):
    _BLACKLIST_PHASHES = [
        # ALL BLACK 512x512
        "0000000000000000",

        # ALL WHITE 512x512
        "8000000000000000"
    ]

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--phash",
            default=False,
            action="store_true",
            required=False,
            help="generate a phase of an image and remove images that are similar or close mostly white or mostly black. "
                 "(default: False)"
        )
        

    def parse_args(self, args: _argparse.Namespace) -> bool:
        return args.phash

    def process(self, image: _FkImage) -> bool:
        working_image = image.image.convert("RGB")
        image_phash = _imagehash.phash(working_image, 8)

        working_image.close()

        for blacklist_hash in ImagePerceptualHashFilter._BLACKLIST_PHASHES:
            if _imagehash.hex_to_hash(blacklist_hash) - image_phash <= 12:
                return False

        return True

    @property
    def priority(self) -> int:
        return 700

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
