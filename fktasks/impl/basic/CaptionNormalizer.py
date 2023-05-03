import argparse as _argparse
import re as _re

from fktasks import FkTask as _FkTask, FkImage as _FkImage, FkTaskIntensiveness as _FkTaskIntensiveness


class CaptionNormalizer(_FkTask):
    # noinspection GrazieInspection
    _TEXT_REPLACEMENT = {
        r"\:(\s+)?\d+(\.\d+)?": " ",  # remove weights ':1' and ':1.0', etc
        r"\\\((\s+)?": "_---",  # replace escaped brackets (
        r"(\s+)?\\\)": "---_",  # replace escaped brackets )
        r"\\\[(\s+)?": "___-",  # replace escaped brackets [
        r"(\s+)?\\\]": "-___",  # replace escaped brackets ]
        r"[\(\)\[\]]": " ",  # remove left over brackets
        "<.+?>": " ",  # remove loras - maybe find a better way to handle loras?
        r"\\": "",  # remove slashes left over from escaped
        r"\:": ", ",  # replace left colons as commas, can't trained merged tags
        r"\|": ", ",  # replace pipes with commas, can't train dynamic or merged tags
        r"\*": " ",  # remove asterisks
        r"\.(?!\w)": ", ",  # remove periods but preserve things like y.o or 1.8
        "[;'\"+]": ", ",  # remove extraneous punctuation
        "[{}]": " ",  # remove brackets
        r"\s+": " ",  # remove extra whitespace
        "_---": "\\(",  # reverse escaped brackets (
        "---_": "\\)",  # reverse escaped brackets )
        "___-": "\\[",  # reverse escaped brackets [
        "-___": "\\]",  # reverse escaped brackets ]
    }

    @classmethod
    def register_args(cls, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--normalize-captions",
            action="store_true",
            default=False,
            required=False,
            help="normalize captions by removing weights, punctuation and extraneous symbols; (default: False)"
        )

    def parse_args(self, args: _argparse.Namespace):
        return args.normalize_captions

    def process(self, image: _FkImage) -> bool:
        caption_text = image.caption_text

        if caption_text:
            caption_text = caption_text.lower()
            for s, r in CaptionNormalizer._TEXT_REPLACEMENT.items():
                caption_text = _re.sub(s, r, caption_text)

            normalized_tags: list[str] = []
            caption_tags: list[str] = caption_text.split(',')

            for caption_tag in caption_tags:
                caption_tag = caption_tag.strip()

                if caption_tag not in normalized_tags:
                    normalized_tags.append(caption_tag)

            if normalized_tags:
                caption_text = ", ".join(normalized_tags).strip()
                image.caption_text = caption_text

        return True

    @property
    def priority(self) -> int:
        return 200

    @property
    def intensiveness(self) -> _FkTaskIntensiveness:
        return _FkTaskIntensiveness.LOW
