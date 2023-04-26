from tasks import FkTask as _FkTask, FkImage as _FkImage


class ImageFilter(_FkTask):

    def __init__(
            self,
            minimum_dimensions: tuple[int, int] = None,
            maximum_dimensions: tuple[int, int] = None,
            modes: list[str] = None
    ):
        if modes is None:
            modes = ["RGB"]

        self.minimum_dimensions = minimum_dimensions
        self.maximum_dimensions = maximum_dimensions
        self.modes = modes

    def process(self, image: _FkImage) -> bool:
        width, height = image.image.size
        mode = image.image.mode

        if mode not in self.modes:
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
