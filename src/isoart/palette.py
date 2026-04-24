"""AW-inspired color palettes for isometric sprites."""

from __future__ import annotations

# Each palette maps role → RGBA tuple

AW_PINE: dict[str, tuple[int, int, int, int]] = {
    "outline":   (15,  45,  15,  255),
    "dark":      (35,  80,  35,  255),
    "mid":       (55,  120, 55,  255),
    "light":     (90,  165, 70,  255),
    "highlight": (145, 210, 110, 255),
    "trunk":     (95,  58,  18,  255),
    "trunk_d":   (60,  35,  10,  255),
}

AW_SNOW_PINE: dict[str, tuple[int, int, int, int]] = {
    "outline":   (50,  80,  100, 255),
    "dark":      (140, 175, 200, 255),
    "mid":       (190, 215, 235, 255),
    "light":     (220, 235, 248, 255),
    "highlight": (245, 250, 255, 255),
    "trunk":     (95,  58,  18,  255),
    "trunk_d":   (60,  35,  10,  255),
}

# AW blue-tint variant (faction tint, as seen in the reference image)
AW_BLUE_PINE: dict[str, tuple[int, int, int, int]] = {
    "outline":   (10,  30,  80,  255),
    "dark":      (30,  75,  155, 255),
    "mid":       (55,  120, 205, 255),
    "light":     (90,  165, 230, 255),
    "highlight": (160, 210, 250, 255),
    "trunk":     (95,  58,  18,  255),
    "trunk_d":   (60,  35,  10,  255),
}

# Neutral grass tile colors
GRASS_LIGHT: tuple[int, int, int, int] = (168, 200, 72, 255)
GRASS_DARK:  tuple[int, int, int, int] = (136, 168, 48, 255)
TILE_OUTLINE: tuple[int, int, int, int] = (88,  120, 24, 255)
