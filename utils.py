KNOWN_IMAGE_EXTENSIONS = [
    ".bmp",
    ".gif",
    ".jpg",
    ".jpeg",
    ".png",
    ".tiff",
    ".webp"
]

KNOWN_CAPTION_TEXT_EXTENSIONS = [
    ".txt",
    ".caption"
]


def format_timestamp(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    return "%02d:%02d:%02d" % (hours, minutes % 60, seconds % 60)
