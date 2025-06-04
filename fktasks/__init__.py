"""Expose common task classes and helpers."""

from fktasks.FkTask import (
    FkImage,
    FkReportableTask,
    FkTask,
    FkTaskIntensiveness,
)
from fktasks.GlobalImageDataCache import GlobalImageDataCache

__all__ = [
    "FkTask",
    "FkImage",
    "FkReportableTask",
    "FkTaskIntensiveness",
    "GlobalImageDataCache",
    "FkPipeline",
]


def __getattr__(name: str):
    if name == "FkPipeline":
        from .FkPipeline import FkPipeline
        return FkPipeline
    raise AttributeError(f"module {__name__} has no attribute {name}")

