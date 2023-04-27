import textwrap

from tasks import FkImage as _FkImage, FkReportableTask as _FkReportableTask


class CaptionFilter(_FkReportableTask):

    def __init__(
            self,
            require_caption_text: bool = True,
            required_tags: list[str] = None,
            blacklist_tags: list[str] = None
    ):
        self.require_caption_text = require_caption_text
        self.required_tags = required_tags
        self.blacklist_tags = blacklist_tags

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

        if self.blacklist_tags:
            blacklist_tag_found = False

            for blacklist_tag in self.blacklist_tags:
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
            wrapped_text = textwrap.fill(tags_text, 42)
            return description, wrapped_text

        if self.required_tags:
            required_tags_report_item = tags_report("Required tags", self.required_tags)
            report_items.append(required_tags_report_item)

        if self.blacklist_tags:
            blacklist_tags_report_item = tags_report("Blacklisted tags", self.blacklist_tags)
            report_items.append(blacklist_tags_report_item)

        return report_items
