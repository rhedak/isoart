"""Terrain sprites — Mountain, House (stubs for future implementation)."""

from __future__ import annotations

from PIL import Image

from .base import IsoSprite


class Mountain(IsoSprite):
    """Isometric mountain sprite (not yet implemented)."""

    def get_anchor(self) -> tuple[int, int]:
        raise NotImplementedError

    def get_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        raise NotImplementedError


class House(IsoSprite):
    """Isometric house/building sprite (not yet implemented)."""

    def get_anchor(self) -> tuple[int, int]:
        raise NotImplementedError

    def get_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        raise NotImplementedError
