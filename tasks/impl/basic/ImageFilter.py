import argparse as _argparse
import textwrap as _textwrap
from typing import Optional as _Optional

from tasks import FkImage as _FkImage, FkReportableTask as _FkReportableTask


class ImageFilter(_FkReportableTask):

    def __init__(
            self,
            minimum_dimensions: tuple[int, int] = None,
            maximum_dimensions: tuple[int, int] = None,
            modes: list[str] = None
    ):
        self.minimum_dimensions = minimum_dimensions
        self.maximum_dimensions = maximum_dimensions
        self.modes = modes

        self._invalid_modes = []

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--minimum-dimensions",
            default=None,
            type=str,
            help="image dimensions must be this size or larger, or be discarded "
                 "(example: 320x320; default: None)"
        )

        arg_parser.add_argument(
            "--maximum-dimensions",
            default=None,
            type=str,
            help="image dimensions must be this size or smaller, or be discarded "
                 "(example: 1024x1024; default: None)"
        )

        arg_parser.add_argument(
            "--modes",
            default=None,
            type=str,
            help="discard image if mode does not match provided modes; "
                 "modes can be provided in a comma-separated list "
                 "(default: None [disabled])"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        if args.minimum_dimensions:
            w = h = args.minimum_dimensions

            if 'x' in args.minimum_dimensions:
                w, h = args.minimum_dimensions.split("x")

            self.minimum_dimensions = (int(w), int(h))

        if args.maximum_dimensions:
            w = h = args.maximum_dimensions
            if 'x' in args.maximum_dimensions:
                w, h = args.maximum_dimensions.split("x")

            self.maximum_dimensions = (int(w), int(h))

        if args.modes:
            self.modes = [t.strip() for t in args.modes.split(",")]

        return not (not self.modes and not self.minimum_dimensions and not self.maximum_dimensions)

    def process(self, image: _FkImage) -> bool:
        width, height = image.image.size
        mode = image.image.mode

        if mode not in self.modes:
            if mode not in self._invalid_modes:
                self._invalid_modes.append(mode)

            return False

        if self.minimum_dimensions:
            min_width, min_height = self.minimum_dimensions
            if width < min_width or height < min_height:
                return False

        if self.maximum_dimensions:
            max_width, max_height = self.maximum_dimensions
            if width > max_width or height > max_height:
                return False

        return True

    def report(self) -> list[tuple[str, any]]:
        report_items: list[_Optional[tuple[str, any]]] = []

        if self.modes:
            tags_text = ", ".join(self.modes).strip()
            wrapped_text = _textwrap.fill(tags_text, 42)
            report_items.append(("Modes", wrapped_text))

        if self.minimum_dimensions:
            min_width, min_height = self.minimum_dimensions
            report_items.append(("Minimum dimensions", f"{min_width}x{min_height}px"))

        if self.maximum_dimensions:
            max_width, max_height = self.maximum_dimensions
            report_items.append(("Maximum dimensions", f"{max_width}x{max_height}px"))

        if len(self._invalid_modes) > 0:
            report_items.append(None)
            report_items.append(("Discarded modes", ", ".join(self._invalid_modes)))

        return report_items

    @property
    def priority(self) -> int:
        return 400
