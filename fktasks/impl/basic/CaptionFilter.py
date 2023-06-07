import argparse as _argparse
import textwrap as _textwrap

import nicegui.element
from nicegui import ui

from fktasks import FkImage as _FkImage, FkReportableTask as _FkReportableTask, FkTaskIntensiveness


class CaptionFilter(_FkReportableTask):

    def __init__(
            self,
            require_caption_text: bool = False,
            required_tags: list[str] = None,
            blacklist_tags: list[str] = None
    ):
        self.require_caption_text = require_caption_text
        self.required_tags = required_tags
        self.blacklisted_tags = blacklist_tags

    @classmethod
    def register_args(cls, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--require-caption-text",
            action="store_true",
            required=False,
            default=False,
            help="require caption text file to exist and be non-empty (default: False)"
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

        requires_tag = self.required_tags is not None and len(self.required_tags)
        has_required_tag = False
        if self.required_tags:
            for required_tag in self.required_tags:
                if required_tag in caption_text:
                    has_required_tag = True
                    break

            if not has_required_tag:
                return False

        if self.blacklisted_tags:
            for blacklist_tag in self.blacklisted_tags:
                if blacklist_tag in caption_text:
                    return False

        return not requires_tag or has_required_tag

    def report(self) -> list[tuple[str, any]]:
        report_items: list[tuple[str, any]] = []
        if self.require_caption_text:
            report_items.append(("Caption text required", self.require_caption_text))

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

    @property
    def intensiveness(self) -> FkTaskIntensiveness:
        return FkTaskIntensiveness.LOW

    @classmethod
    def webui_config(cls, *args, **kwargs) -> tuple[nicegui.element.Element, list[nicegui.element.Element]]:
        with ui.element("div") as element:
            with ui.grid(rows=3):
                whitelist_tags = ui.input("Whitelist Tags", placeholder="Comma-separated list").props("outlined dense")
                blacklist_tags = ui.input("Blacklist Tags", placeholder="Comma-separated list").props("outlined dense")
                require_caption_text = ui.checkbox("Require Caption Text", value=True)

        return element, [whitelist_tags, blacklist_tags, require_caption_text]

    @classmethod
    def webui_name(cls) -> str:
        return "Caption Filter"
