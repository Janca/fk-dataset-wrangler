import inspect as _inspect
import os

import nicegui.element
import nicegui.elements.mixins.value_element

import utils as _utils
from fkio.FkDestination import FkDestination as _FkDestination
from fkio.FkSource import FkSource as _FkSource
from fktasks.FkTask import FkTask


def load_fkio_classes():
    package_path = os.path.join("fkio", "impl")
    _, fkio_classes = _utils.load_modules_and_classes_from_directory(package_path, "fkio.impl")

    source_classes = [cls for cls in fkio_classes if _inspect.isclass(cls) and issubclass(cls, _FkSource)]
    destination_classes = [cls for cls in fkio_classes if _inspect.isclass(cls) and issubclass(cls, _FkDestination)]

    return source_classes, destination_classes


def load_fktask_classes():
    package_path = os.path.join("fktasks", "impl")
    _, package_classes = _utils.load_modules_and_classes_from_directory(package_path, "fktasks.impl")

    clses = [cls for cls in package_classes if issubclass(cls, FkTask)]
    print(clses)

    return clses


def get_values(*value_element: nicegui.element.Element) -> list:
    return [
        v_element.value for v_element in value_element
        if isinstance(v_element, nicegui.elements.mixins.value_element.ValueElement)
    ]
