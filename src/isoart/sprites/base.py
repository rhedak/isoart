"""Abstract base class for all isometric sprites."""

from __future__ import annotations
from abc import ABC, abstractmethod

from PIL import Image


class IsoSprite(ABC):
    """A sprite that can blit itself onto a Pillow RGBA image."""

    @abstractmethod
    def get_anchor(self) -> tuple[int, int]:
        """Pixel offset from blit origin to sprite bottom-center (tile foot)."""
        ...

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        """Bounding box of this sprite in pixels (width, height)."""
        ...

    @abstractmethod
    def blit(self, target: Image.Image, x: int, y: int) -> None:
        """Composite this sprite onto *target* with its foot at (x, y)."""
        ...
