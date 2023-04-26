import PIL.Image as _Pillow

from tasks import FkTask as _FkTask, FkImage as _FkImage


class ImageScaler(_FkTask):
    def __init__(self, max_size: int):
        self.max_size = max_size

    def process(self, image: _FkImage) -> bool:
        width, height = image.image.size

        if width > height and width > self.max_size:
            ratio = height / width

            width = self.max_size
            height = width * ratio

        elif height > width and height > self.max_size:
            ratio = width / height

            height = self.max_size
            width = height * ratio

        elif width == height and width > self.max_size:
            width = self.max_size
            height = self.max_size

        else:
            return True

        width = int(width)
        height = int(height)

        image.image = image.image.resize(
            size=(width, height),
            resample=_Pillow.LANCZOS
        )

        return True
