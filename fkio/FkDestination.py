import abc as _abc

from fktasks.FkTask import FkImage as _FkImage


class FkDestination(_abc.ABC):
    @_abc.abstractmethod
    def save(self, image: _FkImage, image_ext: str, caption_text_ext: str):
        pass
