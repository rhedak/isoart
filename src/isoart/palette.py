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

# Mountain palettes — keys: outline, light, mid, dark, base, base_d
AW_MOUNTAIN: dict[str, tuple[int, int, int, int]] = {
    "outline": (40,  55,  80,  255),
    "light":   (165, 185, 210, 255),
    "mid":     (120, 145, 175, 255),
    "dark":    (80,  100, 130, 255),
    "base":    (95,  115, 145, 255),
    "base_d":  (60,  75,  100, 255),
}

AW_MOUNTAIN_SNOW: dict[str, tuple[int, int, int, int]] = {
    "outline": (80,  100, 120, 255),
    "light":   (240, 245, 255, 255),
    "mid":     (200, 215, 235, 255),
    "dark":    (150, 170, 200, 255),
    "base":    (120, 145, 175, 255),
    "base_d":  (80,  100, 130, 255),
}

# House palettes — keys: outline, roof_l, roof_r, roof_ridge, wall_f, wall_s, window, door
AW_HOUSE_RED: dict[str, tuple[int, int, int, int]] = {
    "outline":    (30,  20,  20,  255),
    "roof_l":     (210, 70,  50,  255),
    "roof_r":     (160, 40,  30,  255),
    "roof_ridge": (240, 110, 80,  255),
    "wall_f":     (230, 215, 185, 255),
    "wall_s":     (185, 170, 145, 255),
    "window":     (130, 185, 220, 255),
    "door":       (120, 80,  40,  255),
}

AW_HOUSE_BLUE: dict[str, tuple[int, int, int, int]] = {
    "outline":    (20,  20,  40,  255),
    "roof_l":     (60,  100, 200, 255),
    "roof_r":     (35,  65,  155, 255),
    "roof_ridge": (100, 145, 230, 255),
    "wall_f":     (220, 225, 240, 255),
    "wall_s":     (175, 180, 200, 255),
    "window":     (130, 185, 220, 255),
    "door":       (80,  80,  140, 255),
}

AW_HOUSE_NEUTRAL: dict[str, tuple[int, int, int, int]] = {
    "outline":    (30,  25,  20,  255),
    "roof_l":     (170, 145, 100, 255),
    "roof_r":     (130, 110, 70,  255),
    "roof_ridge": (200, 175, 130, 255),
    "wall_f":     (230, 215, 185, 255),
    "wall_s":     (185, 170, 145, 255),
    "window":     (130, 185, 220, 255),
    "door":       (120, 80,  40,  255),
}

# Round-tree palettes — keys: outline, dark, mid, light, highlight, trunk, trunk_d
AW_ROUND_TREE: dict[str, tuple[int, int, int, int]] = {
    "outline":   (20,  50,  20,  255),
    "dark":      (45,  100, 45,  255),
    "mid":       (70,  145, 60,  255),
    "light":     (105, 180, 80,  255),
    "highlight": (155, 215, 115, 255),
    "trunk":     (95,  58,  18,  255),
    "trunk_d":   (60,  35,  10,  255),
}

AW_AUTUMN_TREE: dict[str, tuple[int, int, int, int]] = {
    "outline":   (80,  40,  10,  255),
    "dark":      (180, 90,  20,  255),
    "mid":       (220, 140, 30,  255),
    "light":     (240, 185, 60,  255),
    "highlight": (255, 220, 100, 255),
    "trunk":     (95,  58,  18,  255),
    "trunk_d":   (60,  35,  10,  255),
}

AW_BLUE_ROUND_TREE: dict[str, tuple[int, int, int, int]] = {
    "outline":   (10,  35,  80,  255),
    "dark":      (35,  85,  160, 255),
    "mid":       (60,  130, 210, 255),
    "light":     (95,  170, 235, 255),
    "highlight": (160, 215, 255, 255),
    "trunk":     (95,  58,  18,  255),
    "trunk_d":   (60,  35,  10,  255),
}

# Grass tile colors
GRASS_LIGHT:   tuple[int, int, int, int] = (204, 228, 76,  255)
GRASS_DARK:    tuple[int, int, int, int] = (156, 188, 44,  255)
TILE_OUTLINE:  tuple[int, int, int, int] = (96,  130, 24,  255)

# Water tile colors — mid blue with checker variation
WATER_LIGHT:   tuple[int, int, int, int] = (82,  168, 242, 255)
WATER_DARK:    tuple[int, int, int, int] = (56,  132, 214, 255)
WATER_OUTLINE: tuple[int, int, int, int] = (38,  80,  158, 255)

# Beach / sand tile colors
BEACH_LIGHT:   tuple[int, int, int, int] = (250, 230, 155, 255)
BEACH_DARK:    tuple[int, int, int, int] = (215, 188, 100, 255)
BEACH_OUTLINE: tuple[int, int, int, int] = (170, 140, 70,  255)

# Road / paved tile colors
ROAD_LIGHT:    tuple[int, int, int, int] = (185, 185, 185, 255)
ROAD_DARK:     tuple[int, int, int, int] = (145, 145, 145, 255)
ROAD_OUTLINE:  tuple[int, int, int, int] = (85,  85,  85,  255)
ROAD_MARK:     tuple[int, int, int, int] = (215, 215, 215, 255)

# Terrain detail overlay colours
GRASS_TUFT:    tuple[int, int, int, int] = (120, 158, 30,  255)
WATER_SHIMMER: tuple[int, int, int, int] = (140, 200, 255, 255)
BEACH_GRAIN:   tuple[int, int, int, int] = (195, 168, 85,  255)
ROAD_STUD:     tuple[int, int, int, int] = (200, 200, 200, 255)

# Infantry palettes — keys: outline, helmet, body, legs, skin, pack
AW_INFANTRY_RED: dict[str, tuple[int, int, int, int]] = {
    "outline": (50,  15,  15,  255),
    "helmet":  (200, 50,  40,  255),
    "body":    (210, 80,  60,  255),
    "legs":    (140, 40,  30,  255),
    "skin":    (230, 190, 150, 255),
    "pack":    (100, 70,  40,  255),
}

AW_INFANTRY_BLUE: dict[str, tuple[int, int, int, int]] = {
    "outline": (15,  15,  50,  255),
    "helmet":  (50,  90,  200, 255),
    "body":    (70,  120, 215, 255),
    "legs":    (35,  65,  150, 255),
    "skin":    (230, 190, 150, 255),
    "pack":    (50,  60,  100, 255),
}

# Tank / unit palettes — keys: outline, body_l, body_d, turret, barrel, tread
AW_TANK_RED: dict[str, tuple[int, int, int, int]] = {
    "outline": (60,  20,  20,  255),
    "body_l":  (220, 70,  55,  255),
    "body_d":  (160, 40,  35,  255),
    "turret":  (235, 100, 80,  255),
    "barrel":  (60,  55,  55,  255),
    "tread":   (40,  35,  35,  255),
}

AW_TANK_BLUE: dict[str, tuple[int, int, int, int]] = {
    "outline": (20,  20,  60,  255),
    "body_l":  (70,  120, 215, 255),
    "body_d":  (40,  75,  165, 255),
    "turret":  (110, 160, 240, 255),
    "barrel":  (55,  55,  60,  255),
    "tread":   (35,  35,  45,  255),
}
