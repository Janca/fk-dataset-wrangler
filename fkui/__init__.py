"""User interface utilities and widgets."""

import nicegui.element

from fkui.FkWrangler import FkWrangler


def __set_prop(self, key: str, value):
    self._props[key] = value
    self.update()


setattr(nicegui.element.Element, "set_prop", __set_prop)

__all__ = ["FkWrangler"]

