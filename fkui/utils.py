import inspect as _inspect
import os as _os

import utils as _utils
from fkio.FkDestination import FkDestination as _FkDestination
from fkio.FkSource import FkSource as _FkSource


def load_fkio_classes(package_dirpath: str = _os.path.join("fkio", "impl")):
    _, fkio_classes = _utils.load_modules_and_classes_from_directory(package_dirpath)

    source_classes = [cls for cls in fkio_classes if _inspect.isclass(cls) and issubclass(cls, _FkSource)]
    destination_classes = [cls for cls in fkio_classes if _inspect.isclass(cls) and issubclass(cls, _FkDestination)]

    return source_classes, destination_classes
