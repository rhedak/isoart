"""Generate one sample PNG per sprite variant in samples/.

Run from the repo root:
    python samples/generate.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from isoart import (
    AW_AUTUMN_TREE,
    TankLarge,
    AW_BLUE_PINE,
    AW_BLUE_ROUND_TREE,
    AW_HOUSE_BLUE,
    AW_HOUSE_NEUTRAL,
    AW_HOUSE_RED,
    AW_MOUNTAIN,
    AW_MOUNTAIN_SNOW,
    AW_PINE,
    AW_ROUND_TREE,
    AW_SNOW_PINE,
    AW_TANK_BLUE,
    AW_TANK_RED,
    IsoCanvas,
    House,
    Mountain,
    PineTree,
    RoundTree,
    Tank,
    TerrainType,
    TopDownCanvas,
)
from isoart.palette import AW_INFANTRY_BLUE, AW_INFANTRY_RED
from isoart.sprites.units import Infantry
from isoart.sprites.base import IsoSprite

TILE_W, TILE_H = 32, 16
SCALE = 4
OUT = Path(__file__).parent

SPRITES: list[tuple[str, IsoSprite]] = [
    # Pine trees
    ("pine_green",  PineTree(tier_count=3, tier_size=26, palette=AW_PINE)),
    ("pine_snow",   PineTree(tier_count=3, tier_size=26, palette=AW_SNOW_PINE)),
    ("pine_blue",   PineTree(tier_count=3, tier_size=26, palette=AW_BLUE_PINE)),
    ("pine_tall",   PineTree(tier_count=4, tier_size=26, palette=AW_PINE)),
    # Round trees
    ("round_green",  RoundTree(tier_count=3, tier_size=26, palette=AW_ROUND_TREE)),
    ("round_autumn", RoundTree(tier_count=3, tier_size=26, palette=AW_AUTUMN_TREE)),
    ("round_blue",   RoundTree(tier_count=3, tier_size=26, palette=AW_BLUE_ROUND_TREE)),
    # Mountains
    ("mountain",      Mountain(size=24, palette=AW_MOUNTAIN)),
    ("mountain_snow", Mountain(size=24, palette=AW_MOUNTAIN_SNOW)),
    # Houses
    ("house_red",     House(palette=AW_HOUSE_RED)),
    ("house_blue",    House(palette=AW_HOUSE_BLUE)),
    ("house_neutral", House(palette=AW_HOUSE_NEUTRAL)),
    # Tanks
    ("tank_red",  Tank(palette=AW_TANK_RED)),
    ("tank_blue", Tank(palette=AW_TANK_BLUE)),
]


def make_sample(name: str, sprite: IsoSprite) -> None:
    cols, rows = 3, 3
    canvas_w = (cols + rows) * TILE_W // 2 + TILE_W
    canvas_h = (cols + rows) * TILE_H // 2 + TILE_H * 4
    origin = (canvas_w // 2, TILE_H * 2)

    canvas = IsoCanvas(
        canvas_w, canvas_h,
        bg_color=(28, 28, 36, 255),
        tile_w=TILE_W, tile_h=TILE_H,
        origin=origin,
    )
    canvas.draw_grid(cols, rows)
    canvas.draw(sprite, 1, 1)
    canvas.save(str(OUT / f"{name}.png"), scale=SCALE)
    print(f"  {name}.png")


_MAP_LAYOUT = [
    # shoreline + bridge demo
    "GGGBWWBGGG",
    "GGBWWWWBGG",
    "GRRRRRRRRG",
    "GGBWWWWBGG",
    "GGGBWWBGGG",
]


def _decode_map() -> list[list[TerrainType]]:
    legend = {
        "G": TerrainType.GRASS,
        "B": TerrainType.BEACH,
        "W": TerrainType.WATER,
        "R": TerrainType.ROAD,
    }
    return [[legend[c] for c in row] for row in _MAP_LAYOUT]


def make_terrain_preview() -> None:
    """Iso diamond-tile terrain preview."""
    tiles = _decode_map()
    cols, rows = len(tiles[0]), len(tiles)
    tw, th = 32, 16
    w = (cols + rows) * tw // 2 + 40
    h = (cols + rows) * th // 2 + 40
    canvas = IsoCanvas(
        w, h, bg_color=(28, 28, 36, 255),
        tile_w=tw, tile_h=th, origin=(w // 2, 20),
    )
    canvas.draw_map(tiles)
    canvas.save(str(OUT / "terrain_preview.png"), scale=SCALE)
    print("  terrain_preview.png")


def make_topdown_preview() -> None:
    """Top-down square-tile terrain preview (AW-style)."""
    tiles = _decode_map()
    cols, rows = len(tiles[0]), len(tiles)
    ts = 20
    pad = 16
    w = cols * ts + pad * 2
    h = rows * ts + pad * 2
    canvas = TopDownCanvas(
        w, h, bg_color=(28, 28, 36, 255),
        tile_size=ts, origin=(pad, pad),
    )
    canvas.draw_map(tiles)
    canvas.save(str(OUT / "topdown_preview.png"), scale=SCALE)
    print("  topdown_preview.png")


def make_unit_sample(name: str, *sprites: IsoSprite) -> None:
    """Render one or more unit sprites on a small top-down grass tile grid.

    Uses TopDownCanvas (the real usage context) at 8× scale so individual
    pixels are easy to inspect.
    """
    ts = 24
    pad = 12
    cols, rows = max(3, len(sprites) * 2), 3
    w = cols * ts + pad * 2
    h = rows * ts + pad * 2
    canvas = TopDownCanvas(
        w, h,
        bg_color=(28, 28, 36, 255),
        tile_size=ts,
        origin=(pad, pad),
        tile_outline=None,
    )
    tiles = [[TerrainType.GRASS] * cols for _ in range(rows)]
    canvas.draw_map(tiles)
    canvas.draw_terrain_details(tiles)

    # Space sprites evenly across the middle row
    for i, sprite in enumerate(sprites):
        gx = 1 + i * 2 if len(sprites) > 1 else cols // 2
        canvas.draw(sprite, gx, 1)

    canvas.save(str(OUT / f"{name}.png"), scale=8)
    print(f"  {name}.png")


if __name__ == "__main__":
    print(f"Writing to {OUT}/")
    for name, sprite in SPRITES:
        make_sample(name, sprite)
    make_terrain_preview()
    make_topdown_preview()
    # Unit close-ups on top-down canvas at 8×
    make_unit_sample("tank_red_td",  Tank(palette=AW_TANK_RED))
    make_unit_sample("tank_blue_td", Tank(palette=AW_TANK_BLUE))
    make_unit_sample("tanks_both",   Tank(palette=AW_TANK_RED), Tank(palette=AW_TANK_BLUE))
    make_unit_sample("infantry_red_td",  Infantry(palette=AW_INFANTRY_RED))
    make_unit_sample("infantry_blue_td", Infantry(palette=AW_INFANTRY_BLUE))
    # TankLarge close-ups
    make_unit_sample("tank_large_red_td",  TankLarge(palette=AW_TANK_RED))
    make_unit_sample("tank_large_blue_td", TankLarge(palette=AW_TANK_BLUE))
    make_unit_sample("tank_large_both",    TankLarge(palette=AW_TANK_RED), TankLarge(palette=AW_TANK_BLUE))
    print("Done.")
