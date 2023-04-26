from tasks import FkTask as _FkTask, FkImage as _FkImage


class CaptionFilter(_FkTask):

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

        if not caption_text and self.require_caption_text:
            return False

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
