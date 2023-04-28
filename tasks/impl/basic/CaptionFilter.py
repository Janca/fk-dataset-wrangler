import argparse as _argparse
import textwrap as _textwrap

from tasks import FkImage as _FkImage, FkReportableTask as _FkReportableTask


class CaptionFilter(_FkReportableTask):

    def __init__(
            self,
            require_caption_text: bool = False,
            required_tags: list[str] = None,
            blacklist_tags: list[str] = None
    ):
        self.require_caption_text = require_caption_text
        self.required_tags = required_tags
        self.blacklist_tags = blacklist_tags

    @classmethod
    def register_args(cls, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--require-caption-text",
            action="store_true",
            required=False,
            default=False,
            help="require caption text file to exist and be non-empty (default: True)"
        )

        arg_parser.add_argument(
            "--required-tags",
            required=False,
            default=None,
            help="discard image if the caption text does not contain one or more of the provided tags; "
                 "tags can be provided in a comma-separated list (default: None)"
        )

        arg_parser.add_argument(
            "--blacklisted-tags",
            required=False,
            default=None,
            help="discard image if the caption text contains one or more of the provided tags; "
                 "tags can be provided in a comma-separated list (default: None)"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        self.require_caption_text = args.require_caption_text

        if args.required_tags:
            self.required_tags = [t.strip() for t in args.required_tags.split(",")]

        if args.blacklisted_tags:
            self.blacklisted_tags = [t.strip() for t in args.blacklisted_tags.split(",")]

        return self.require_caption_text or self.required_tags or self.blacklisted_tags

    def process(self, image: _FkImage) -> bool:
        caption_text = image.caption_text

        if not caption_text:
            return not self.require_caption_text

        if self.required_tags:
            required_tag_found = False

            for required_tag in self.required_tags:
                if required_tag in caption_text:
                    required_tag_found = True
                    break

            if not required_tag_found:
                return False

        if self.blacklisted_tags:
            blacklist_tag_found = False

            for blacklist_tag in self.blacklisted_tags:
                if blacklist_tag in caption_text:
                    blacklist_tag_found = True
                    break

            if blacklist_tag_found:
                return False

        return True

    def report(self) -> list[tuple[str, any]]:
        report_items: list[tuple[str, any]] = []
        if self.require_caption_text:
            report_items.append(("Caption text required", self.required_tags))

        def tags_report(description: str, tags: list[str]) -> tuple[str, any]:
            tags_text = ", ".join(tags).strip()
            wrapped_text = _textwrap.fill(tags_text, 42, subsequent_indent="    ")
            return description, wrapped_text

        if self.required_tags:
            required_tags_report_item = tags_report("Required tags", self.required_tags)
            report_items.append(required_tags_report_item)

        if self.blacklisted_tags:
            blacklist_tags_report_item = tags_report("Blacklisted tags", self.blacklisted_tags)
            report_items.append(blacklist_tags_report_item)

        return report_items

    @property
    def priority(self) -> int:
        return 100
