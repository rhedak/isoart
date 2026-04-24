"""Isometric coordinate transforms (dimetric 2:1 projection)."""

from __future__ import annotations


def world_to_screen(
    gx: float,
    gy: float,
    gz: float = 0,
    tile_w: int = 32,
    tile_h: int = 16,
) -> tuple[int, int]:
    """Convert grid (gx, gy, gz) to screen pixel (sx, sy).

    Origin is at screen top-center of the grid.
    Positive gz raises the sprite upward.
    """
    sx = (gx - gy) * (tile_w // 2)
    sy = (gx + gy) * (tile_h // 2) - int(gz * tile_h)
    return int(sx), int(sy)


def screen_to_world(
    sx: int,
    sy: int,
    tile_w: int = 32,
    tile_h: int = 16,
) -> tuple[float, float]:
    """Inverse of world_to_screen (gz=0 plane only)."""
    half_w = tile_w / 2
    half_h = tile_h / 2
    gx = (sx / half_w + sy / half_h) / 2
    gy = (sy / half_h - sx / half_w) / 2
    return gx, gy


def tile_diamond(
    gx: float,
    gy: float,
    tile_w: int = 32,
    tile_h: int = 16,
    origin: tuple[int, int] = (0, 0),
) -> list[tuple[int, int]]:
    """Return the four screen vertices of a flat iso tile diamond."""
    cx, cy = world_to_screen(gx, gy, 0, tile_w, tile_h)
    cx += origin[0]
    cy += origin[1]
    hw = tile_w // 2
    hh = tile_h // 2
    return [
        (cx,      cy - hh),  # top
        (cx + hw, cy),        # right
        (cx,      cy + hh),  # bottom
        (cx - hw, cy),        # left
    ]
