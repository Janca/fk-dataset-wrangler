from typing import Optional, Callable

from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.elements.mixins.value_element import ValueElement


class Range(ValueElement, DisableableElement):

    def __init__(
            self,
            min: float,
            max: float,
            step: float = 1.0,
            value: Optional[dict[str, float]] = None,
            on_change: Optional[Callable] = None
    ) -> None:
        """Slider

        :param min: lower bound of the slider
        :param max: upper bound of the slider
        :param step: step size
        :param value: initial value to set position of the slider
        :param on_change: callback which is invoked when the user releases the slider
        """
        super().__init__(tag='q-range', value=value, on_value_change=on_change, throttle=0.05)
        self._props['min'] = min
        self._props['max'] = max
        self._props['step'] = step
