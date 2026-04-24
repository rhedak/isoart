"""AW Dogfights-inspired PoC scene.

Generates ``aw_dogfights.png``: an Advance-Wars-style battle map with
top-down terrain tiles and iso-perspective sprites on top. Red base on
the west, blue base on the east, a zigzagging water channel between
them, mountain chains along the east coast + NW corner, forest
patches on both sides.
"""

from __future__ import annotations

from pathlib import Path

from isoart import (
    AW_AUTUMN_TREE,
    AW_BLUE_PINE,
    AW_BLUE_ROUND_TREE,
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
# Terrain layout: 24x16, water channel zig-zags 1 tile west halfway down
# ---------------------------------------------------------------------------
# Legend: G=grass, B=beach, W=water, R=road
_MAP = [
    "GGGGGGGGGGGBWWBGGGGGGGGG",  # 0
    "GGGGGGGGGGGBWWBGGGGGGGGG",  # 1
    "GGGGGGGGGGGBWWBGGGGGGGGG",  # 2
    "GGGGGGGGGGGBWWBGGGGGGGGG",  # 3
    "GGGGGGGGGGGBWWBGGGGGGGGG",  # 4
    "GGGGGGRRRRRBWWBRRRRRGGGG",  # 5 — bridge + approach roads
    "GGGGGGGGGGGBWWBGGGGGGGGG",  # 6
    "GGGGGGGGGGBBWWBGGGGGGGGG",  # 7 — coast starts bending west
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 8 — channel 1 tile west
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 9
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 10
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 11
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 12
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 13
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 14
    "GGGGGGGGGGBWWBGGGGGGGGGG",  # 15
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
# Sprite factories (smaller-than-default sizes for tile-matched scale)
# ---------------------------------------------------------------------------


def _pine(palette=AW_PINE) -> PineTree:
    return PineTree(tier_count=3, tier_size=14, palette=palette)


def _round_tree(palette=AW_ROUND_TREE) -> RoundTree:
    return RoundTree(tier_size=14, palette=palette)


def _mountain(snow: bool = False) -> Mountain:
    return Mountain(size=16, palette=AW_MOUNTAIN_SNOW if snow else AW_MOUNTAIN)


def _house(red: bool) -> House:
    return House(
        width=14, depth=10, wall_h=12, roof_h=4,
        palette=AW_HOUSE_RED if red else AW_HOUSE_BLUE,
    )


def _tank(red: bool) -> Tank:
    return Tank(scale=0.7, palette=AW_TANK_RED if red else AW_TANK_BLUE)


# ---------------------------------------------------------------------------
# Scene placements — (sprite, gx, gy), drawn back-to-front by gy
# ---------------------------------------------------------------------------


def _scene_sprites() -> list[tuple[object, int, int]]:
    P: list[tuple[object, int, int]] = []

    # --- Mountain chain along the east coast (asymmetric, matches reference) ---
    east_chain = [
        (23, 0, True),  (22, 0, False), (23, 1, False),
        (23, 2, True),  (22, 3, False),
        (23, 4, False), (22, 5, True),
        (23, 6, False), (23, 8, True),
        (22, 10, False), (23, 11, True),
        (22, 13, False), (23, 14, False), (23, 15, True),
    ]
    for gx, gy, snow in east_chain:
        P.append((_mountain(snow), gx, gy))

    # --- Small mountain cluster NW corner ---
    for gx, gy, snow in [(0, 0, True), (1, 0, False), (0, 1, False), (0, 2, True)]:
        P.append((_mountain(snow), gx, gy))

    # --- West forest patch 1: pines near the red base (top-left area) ---
    for gx, gy in [(5, 1), (6, 1), (7, 1), (5, 2), (6, 2), (7, 2)]:
        P.append((_pine(AW_PINE), gx, gy))

    # --- West forest patch 2: round trees south of the base ---
    for gx, gy in [(2, 11), (3, 11), (2, 12), (3, 12), (4, 11)]:
        P.append((_round_tree(AW_ROUND_TREE), gx, gy))
    # Autumn accent
    P.append((_round_tree(AW_AUTUMN_TREE), 4, 12))

    # --- West singletons (scattered variety) ---
    P.extend([
        (_pine(AW_PINE), 8, 8),
        (_round_tree(AW_AUTUMN_TREE), 7, 14),
        (_pine(AW_PINE), 3, 8),
    ])

    # --- East forest patch: big mixed patch above the blue base ---
    for gx, gy in [(17, 1), (18, 1), (19, 1), (17, 2), (18, 2), (19, 2)]:
        P.append((_pine(AW_BLUE_PINE), gx, gy))
    P.append((_round_tree(AW_ROUND_TREE), 16, 2))

    # --- East singletons ---
    P.extend([
        (_round_tree(AW_BLUE_ROUND_TREE), 16, 9),
        (_round_tree(AW_ROUND_TREE), 19, 11),
        (_pine(AW_BLUE_PINE), 17, 13),
        (_pine(AW_BLUE_PINE), 20, 14),
    ])

    # --- Red base: L-shaped house cluster on the west ---
    for gx, gy in [(2, 4), (3, 4), (2, 5), (4, 5), (2, 6)]:
        P.append((_house(red=True), gx, gy))

    # --- Blue base: L-shape mirrored on the east ---
    for gx, gy in [(20, 4), (21, 4), (21, 5), (19, 5), (21, 6)]:
        P.append((_house(red=False), gx, gy))

    # --- Red tanks: 6, clustered near base with 2 forward on the bridge road ---
    for gx, gy in [(5, 3), (6, 4), (4, 6), (5, 6), (8, 5), (9, 5)]:
        P.append((_tank(red=True), gx, gy))

    # --- Blue tanks: 6, mirroring red ---
    for gx, gy in [(18, 3), (17, 4), (18, 6), (19, 6), (15, 5), (16, 5)]:
        P.append((_tank(red=False), gx, gy))

    return P


# ---------------------------------------------------------------------------
# Compose + save
# ---------------------------------------------------------------------------


def main() -> None:
    ts = 18
    pad = 20
    w = _COLS * ts + pad * 2
    h = _ROWS * ts + pad * 2

    canvas = TopDownCanvas(
        w, h,
        bg_color=(28, 28, 36, 255),
        tile_size=ts,
        origin=(pad, pad),
        tile_outline="soft",
    )

    canvas.draw_map(_decode_map())

    # Back-to-front so sprites at larger gy occlude earlier ones
    sprites = _scene_sprites()
    sprites.sort(key=lambda s: (s[2], s[1]))
    for sprite, gx, gy in sprites:
        canvas.draw(sprite, gx, gy)

    canvas.save(str(OUT), scale=2)
    print(f"Saved {OUT} ({len(sprites)} sprites placed)")


if __name__ == "__main__":
    main()
