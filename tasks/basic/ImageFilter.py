import textwrap

from tasks import FkImage as _FkImage, FkReportableTask as _FkReportableTask


class ImageFilter(_FkReportableTask):

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

    def report(self) -> list[tuple[str, any]]:
        report_items: list[tuple[str, any]] = []

        if self.modes:
            tags_text = ", ".join(self.modes).strip()
            wrapped_text = textwrap.fill(tags_text, 42)
            report_items.append(("Modes", wrapped_text))

        if self.minimum_dimensions:
            min_width, min_height = self.minimum_dimensions
            report_items.append(("Minimum dimensions", f"{min_width}x{min_height}px"))

        if self.maximum_dimensions:
            max_width, max_height = self.maximum_dimensions
            report_items.append(("Maximum dimensions", f"{max_width}x{max_height}px"))

        return report_items
