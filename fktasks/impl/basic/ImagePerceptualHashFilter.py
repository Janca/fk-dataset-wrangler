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

    def parse_args(self, args: _argparse.Namespace) -> bool:
        return False

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
