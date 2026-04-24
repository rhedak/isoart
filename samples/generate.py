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
    IsoCanvas,
    House,
    Mountain,
    PineTree,
    RoundTree,
)
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


if __name__ == "__main__":
    print(f"Writing to {OUT}/")
    for name, sprite in SPRITES:
        make_sample(name, sprite)
    print("Done.")
