import inspect as _inspect

import nicegui.element
import nicegui.elements.mixins.value_element

import utils as _utils
from fkio.FkDestination import FkDestination as _FkDestination
from fkio.FkSource import FkSource as _FkSource


def load_fkio_classes():
    _, fkio_classes = _utils.load_modules_and_classes_from_directory("fkio.impl")

    source_classes = [cls for cls in fkio_classes if _inspect.isclass(cls) and issubclass(cls, _FkSource)]
    destination_classes = [cls for cls in fkio_classes if _inspect.isclass(cls) and issubclass(cls, _FkDestination)]

    return source_classes, destination_classes


def get_values(*value_element: nicegui.element.Element) -> list:
    return [
        v_element.value for v_element in value_element
        if isinstance(v_element, nicegui.elements.mixins.value_element.ValueElement)
    ]
