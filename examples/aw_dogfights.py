"""AW Dogfights-inspired PoC scene.

Generates ``aw_dogfights.png``: an Advance-Wars-style battle map with
top-down terrain tiles and iso-perspective sprites on top. Red base on
the left, blue base on the right, water channel in the middle,
mountains along the top/right edges, forests scattered across both
land masses.
"""

from __future__ import annotations

from pathlib import Path

from isoart import (
    AW_AUTUMN_TREE,
    AW_BLUE_PINE,
    AW_HOUSE_BLUE,
    AW_HOUSE_RED,
    AW_MOUNTAIN,
    AW_MOUNTAIN_SNOW,
    AW_PINE,
    AW_ROUND_TREE,
    AW_TANK_BLUE,
    AW_TANK_RED,
    House,
    Mountain,
    PineTree,
    RoundTree,
    Tank,
    TerrainType,
    TopDownCanvas,
)

OUT = Path(__file__).resolve().parent / "aw_dogfights.png"

# ---------------------------------------------------------------------------
# Terrain layout
# ---------------------------------------------------------------------------
# Legend: G=grass, B=beach, W=water, R=road
_MAP = [
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGRRRRBWWBRRRRGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
    "GGGGGGGGBWWBGGGGGGGG",
]
_COLS, _ROWS = len(_MAP[0]), len(_MAP)


def _decode_map() -> list[list[TerrainType]]:
    legend = {
        "G": TerrainType.GRASS,
        "B": TerrainType.BEACH,
        "W": TerrainType.WATER,
        "R": TerrainType.ROAD,
    }
    return [[legend[c] for c in row] for row in _MAP]


# ---------------------------------------------------------------------------
# Sprite placements — (sprite, gx, gy), drawn back-to-front by gy
# ---------------------------------------------------------------------------


def _scene_sprites() -> list[tuple[object, int, int]]:
    placements: list[tuple[object, int, int]] = []

    # ---- Mountains along the top row and along the right edge ----
    placements += [
        (Mountain(size=20, palette=AW_MOUNTAIN),      0,  0),
        (Mountain(size=20, palette=AW_MOUNTAIN_SNOW), 1,  0),
        (Mountain(size=20, palette=AW_MOUNTAIN),     18,  0),
        (Mountain(size=20, palette=AW_MOUNTAIN_SNOW), 19, 0),
        (Mountain(size=20, palette=AW_MOUNTAIN),     19,  2),
        (Mountain(size=20, palette=AW_MOUNTAIN_SNOW), 19, 4),
        (Mountain(size=20, palette=AW_MOUNTAIN),     19,  9),
        (Mountain(size=20, palette=AW_MOUNTAIN),     18, 11),
        (Mountain(size=20, palette=AW_MOUNTAIN_SNOW), 0, 10),
        (Mountain(size=20, palette=AW_MOUNTAIN),      0,  7),
    ]

    # ---- Red-side trees (pines on the western land mass) ----
    placements += [
        (PineTree(tier_size=18, palette=AW_PINE),       2,  1),
        (PineTree(tier_size=18, palette=AW_PINE),       5,  2),
        (PineTree(tier_size=18, palette=AW_PINE),       1,  3),
        (PineTree(tier_size=18, palette=AW_PINE),       6,  8),
        (RoundTree(tier_size=18, palette=AW_ROUND_TREE),3,  9),
        (RoundTree(tier_size=18, palette=AW_AUTUMN_TREE),7, 10),
        (PineTree(tier_size=18, palette=AW_PINE),       1, 11),
    ]

    # ---- Blue-side trees (blue pines + round trees on the eastern mass) ----
    placements += [
        (PineTree(tier_size=18, palette=AW_BLUE_PINE),  13,  1),
        (PineTree(tier_size=18, palette=AW_BLUE_PINE),  16,  2),
        (RoundTree(tier_size=18, palette=AW_ROUND_TREE),14,  3),
        (PineTree(tier_size=18, palette=AW_BLUE_PINE),  17,  7),
        (RoundTree(tier_size=18, palette=AW_ROUND_TREE),13,  9),
        (PineTree(tier_size=18, palette=AW_BLUE_PINE),  15, 10),
        (RoundTree(tier_size=18, palette=AW_AUTUMN_TREE),18,8),
    ]

    # ---- Red base: cluster of red houses on the west ----
    placements += [
        (House(palette=AW_HOUSE_RED), 2,  5),
        (House(palette=AW_HOUSE_RED), 3,  5),
        (House(palette=AW_HOUSE_RED), 2,  6),
        (House(palette=AW_HOUSE_RED), 3,  7),
    ]

    # ---- Blue base: cluster of blue houses on the east ----
    placements += [
        (House(palette=AW_HOUSE_BLUE), 16, 5),
        (House(palette=AW_HOUSE_BLUE), 17, 5),
        (House(palette=AW_HOUSE_BLUE), 16, 6),
        (House(palette=AW_HOUSE_BLUE), 17, 7),
    ]

    # ---- Tanks: 4 red on the west, 4 blue on the east ----
    placements += [
        (Tank(palette=AW_TANK_RED), 5,  4),
        (Tank(palette=AW_TANK_RED), 6,  5),
        (Tank(palette=AW_TANK_RED), 4,  6),
        (Tank(palette=AW_TANK_RED), 5,  7),
    ]
    placements += [
        (Tank(palette=AW_TANK_BLUE), 13, 4),
        (Tank(palette=AW_TANK_BLUE), 14, 5),
        (Tank(palette=AW_TANK_BLUE), 15, 6),
        (Tank(palette=AW_TANK_BLUE), 14, 7),
    ]

    return placements


# ---------------------------------------------------------------------------
# Compose + save
# ---------------------------------------------------------------------------


def main() -> None:
    ts = 22
    pad = 24
    w = _COLS * ts + pad * 2
    h = _ROWS * ts + pad * 2

    canvas = TopDownCanvas(
        w, h,
        bg_color=(28, 28, 36, 255),
        tile_size=ts,
        origin=(pad, pad),
    )

    canvas.draw_map(_decode_map())

    # Back-to-front draw order so sprites at larger gy occlude earlier ones
    sprites = _scene_sprites()
    sprites.sort(key=lambda s: (s[2], s[1]))
    for sprite, gx, gy in sprites:
        canvas.draw(sprite, gx, gy)

    canvas.save(str(OUT), scale=2)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
