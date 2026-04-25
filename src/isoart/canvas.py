"""IsoCanvas — the main drawing surface."""

from __future__ import annotations

from enum import Enum

from PIL import Image, ImageDraw

from .palette import (
    BEACH_DARK,
    BEACH_GRAIN,
    BEACH_LIGHT,
    BEACH_OUTLINE,
    GRASS_DARK,
    GRASS_LIGHT,
    GRASS_TUFT,
    ROAD_DARK,
    ROAD_LIGHT,
    ROAD_MARK,
    ROAD_OUTLINE,
    ROAD_STUD,
    TILE_OUTLINE,
    WATER_DARK,
    WATER_LIGHT,
    WATER_OUTLINE,
    WATER_SHIMMER,
)
from .sprites.base import IsoSprite
from .sprites.terrain import _darken
from .transform import tile_diamond, world_to_screen


def _lerp_color(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
    t: float,
) -> tuple[int, int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))  # type: ignore[return-value]


def _tile_tone(gx: int, gy: int) -> float:
    """Return a 0..1 tone blend for tile (gx, gy).

    Uses a two-level hash so same-tone tiles cluster in patches of ~4 tiles
    rather than alternating every tile. Value 0 → light, 1 → dark.
    """
    zone_x = gx // 4
    zone_y = gy // 4
    zone_hash = (zone_x * 31 + zone_y * 17) % 8
    local_hash = (gx * 7 + gy * 13) % 4
    raw = (zone_hash * 4 + local_hash) % 16
    return raw / 24.0  # keep amplitude low — max ~0.67 blend toward dark


def _proximity_bias(
    tiles: list[list[TerrainType]],
    gx: int,
    gy: int,
    tile_type: TerrainType,
) -> float:
    """Return a small extra dark-blend (0..0.15) based on map neighbourhood.

    Rules:
    - Grass/beach adjacent to water: +0.10 (damp shadow near water edge)
    - Road adjacent to grass/beach: +0.05 (road edge slightly soiled)
    - Otherwise: 0
    """
    rows = len(tiles)
    cols = len(tiles[0]) if rows else 0

    def _type(tx: int, ty: int) -> TerrainType | None:
        if 0 <= ty < rows and 0 <= tx < cols:
            return tiles[ty][tx]
        return None

    neighbours = [
        _type(gx - 1, gy), _type(gx + 1, gy),
        _type(gx, gy - 1), _type(gx, gy + 1),
    ]

    if tile_type in (TerrainType.GRASS, TerrainType.BEACH):
        if TerrainType.WATER in neighbours:
            return 0.10
    if tile_type is TerrainType.ROAD:
        if any(n in (TerrainType.GRASS, TerrainType.BEACH) for n in neighbours if n):
            return 0.05
    return 0.0


class TerrainType(Enum):
    """Terrain tile variants for ``IsoCanvas.draw_tile`` / ``draw_map``."""

    GRASS = "grass"
    WATER = "water"
    BEACH = "beach"
    ROAD = "road"


# (light, dark, outline) per terrain type.
_TERRAIN_PALETTE: dict[
    TerrainType,
    tuple[
        tuple[int, int, int, int],
        tuple[int, int, int, int],
        tuple[int, int, int, int],
    ],
] = {
    TerrainType.GRASS: (GRASS_LIGHT, GRASS_DARK, TILE_OUTLINE),
    TerrainType.WATER: (WATER_LIGHT, WATER_DARK, WATER_OUTLINE),
    TerrainType.BEACH: (BEACH_LIGHT, BEACH_DARK, BEACH_OUTLINE),
    TerrainType.ROAD: (ROAD_LIGHT, ROAD_DARK, ROAD_OUTLINE),
}


class IsoCanvas:
    """An RGBA pixel canvas with iso-grid coordinate support.

    Parameters
    ----------
    width, height:
        Canvas size in pixels.
    bg_color:
        Background fill (RGBA). Default transparent.
    tile_w, tile_h:
        Tile diamond dimensions used for coordinate transforms.
    origin:
        Screen pixel position of grid origin (0, 0) — defaults to top-center.
    """

    def __init__(
        self,
        width: int,
        height: int,
        bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
        tile_w: int = 32,
        tile_h: int = 16,
        origin: tuple[int, int] | None = None,
    ) -> None:
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.image = Image.new("RGBA", (width, height), bg_color)
        self.origin = origin if origin is not None else (width // 2, tile_h)

    # ------------------------------------------------------------------
    # Grid drawing
    # ------------------------------------------------------------------

    def draw_grid(
        self,
        cols: int,
        rows: int,
        color_a: tuple[int, int, int, int] = GRASS_LIGHT,
        color_b: tuple[int, int, int, int] = GRASS_DARK,
        outline: tuple[int, int, int, int] = TILE_OUTLINE,
    ) -> None:
        """Draw a checkerboard iso grid of diamond tiles."""
        draw = ImageDraw.Draw(self.image)
        for gy in range(rows):
            for gx in range(cols):
                verts = tile_diamond(gx, gy, self.tile_w, self.tile_h, self.origin)
                color = color_a if (gx + gy) % 2 == 0 else color_b
                draw.polygon(verts, fill=color, outline=outline)

    def draw_tile(
        self,
        tile_type: TerrainType,
        gx: int,
        gy: int,
    ) -> None:
        """Paint a single diamond tile of the given terrain type.

        Uses a subtle checker variation (light vs dark tone based on
        ``(gx + gy) % 2``) so adjacent tiles don't read as one flat slab.
        """
        light, dark, outline = _TERRAIN_PALETTE[tile_type]
        color = light if (gx + gy) % 2 == 0 else dark
        verts = tile_diamond(gx, gy, self.tile_w, self.tile_h, self.origin)
        ImageDraw.Draw(self.image).polygon(verts, fill=color, outline=outline)

    def draw_map(
        self,
        tiles: list[list[TerrainType]],
    ) -> None:
        """Paint a 2-D terrain map. ``tiles[gy][gx]`` gives the tile type."""
        for gy, row in enumerate(tiles):
            for gx, tile_type in enumerate(row):
                self.draw_tile(tile_type, gx, gy)

    # ------------------------------------------------------------------
    # Sprite drawing
    # ------------------------------------------------------------------

    def draw(
        self,
        sprite: IsoSprite,
        gx: float,
        gy: float,
        gz: float = 0,
    ) -> None:
        """Place a sprite with its tile-foot at grid position (gx, gy, gz)."""
        sx, sy = world_to_screen(gx, gy, gz, self.tile_w, self.tile_h)
        # Foot of the sprite sits at the bottom-center of the tile top face
        foot_x = self.origin[0] + sx
        foot_y = self.origin[1] + sy + self.tile_h // 2
        sprite.blit(self.image, foot_x, foot_y)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def save(self, path: str, scale: int = 1) -> None:
        """Save canvas to *path* as PNG. *scale* uses nearest-neighbor upscale."""
        img = self.image
        if scale != 1:
            w, h = img.size
            img = img.resize((w * scale, h * scale), Image.NEAREST)
        img.save(path)

    def get_image(self) -> Image.Image:
        return self.image


class TopDownCanvas:
    """Top-down square-tile canvas for AW-style maps.

    Terrain tiles render as squares on an orthogonal grid (no iso
    projection for the ground). Sprites still use their iso pixel-art
    geometry — they sit at the visual centre-bottom of a tile, so
    occlusion and shading read correctly even though the ground is
    flat.

    This is the right projection for game-screen-style maps where
    tiles should read as a flat top-down board. Use :class:`IsoCanvas`
    instead when you want diamond-tile iso terrain.

    Parameters
    ----------
    tile_outline:
        Controls how adjacent tiles are separated. AW-style maps want
        subtle seams, not a chess-board grid.

        * ``"soft"`` (default): 1-px border darkened ~15% from the tile's
          own fill color — reads as a gentle shadow rather than a line.
        * ``"hard"``: the terrain's palette ``outline`` color (near-black).
          Useful for debugging or a board-game look.
        * ``None`` or ``False``: no outline at all — tiles butt up
          against each other seamlessly.
    """

    def __init__(
        self,
        width: int,
        height: int,
        bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
        tile_size: int = 24,
        origin: tuple[int, int] = (0, 0),
        tile_outline: str | bool | None = "soft",
    ) -> None:
        self.tile_size = tile_size
        self.image = Image.new("RGBA", (width, height), bg_color)
        self.origin = origin
        self.tile_outline = tile_outline

    # ------------------------------------------------------------------
    # Terrain
    # ------------------------------------------------------------------

    def draw_tile(
        self,
        tile_type: TerrainType,
        gx: int,
        gy: int,
        _extra_dark: float = 0.0,
    ) -> None:
        """Paint a single square tile of the given terrain type."""
        light, dark, outline = _TERRAIN_PALETTE[tile_type]
        fill = _lerp_color(light, dark, min(1.0, _tile_tone(gx, gy) + _extra_dark))
        ts = self.tile_size
        x0 = self.origin[0] + gx * ts
        y0 = self.origin[1] + gy * ts
        draw = ImageDraw.Draw(self.image)

        if self.tile_outline == "soft":
            tile_out: tuple[int, int, int, int] | None = _darken(fill, 0.15)
        elif self.tile_outline == "hard":
            tile_out = outline
        else:
            tile_out = None

        draw.rectangle([x0, y0, x0 + ts - 1, y0 + ts - 1], fill=fill, outline=tile_out)

    def draw_map(
        self,
        tiles: list[list[TerrainType]],
    ) -> None:
        """Paint a 2-D terrain map. ``tiles[gy][gx]`` gives the tile type."""
        for gy, row in enumerate(tiles):
            for gx, tile_type in enumerate(row):
                bias = _proximity_bias(tiles, gx, gy, tile_type)
                self.draw_tile(tile_type, gx, gy, _extra_dark=bias)

    def draw_road_markings(self, tiles: list[list[TerrainType]]) -> None:
        """Draw directional centre-line markings over already-painted road tiles.

        Call after ``draw_map``. Analyses each road tile's N/S/E/W neighbours
        and draws a dashed centre stripe along every road-road axis.
        """
        rows = len(tiles)
        cols = len(tiles[0]) if rows else 0
        ts = self.tile_size
        draw = ImageDraw.Draw(self.image)

        def _is_road(gx: int, gy: int) -> bool:
            if 0 <= gy < rows and 0 <= gx < cols:
                return tiles[gy][gx] is TerrainType.ROAD
            return False

        for gy, row in enumerate(tiles):
            for gx, tile_type in enumerate(row):
                if tile_type is not TerrainType.ROAD:
                    continue

                x0 = self.origin[0] + gx * ts
                y0 = self.origin[1] + gy * ts
                cx = x0 + ts // 2
                cy = y0 + ts // 2

                has_n = _is_road(gx, gy - 1)
                has_s = _is_road(gx, gy + 1)
                has_e = _is_road(gx + 1, gy)
                has_w = _is_road(gx - 1, gy)

                # NS stripe — dashed vertical line at tile centre x
                if has_n or has_s:
                    y_start = y0 + 1
                    y_end   = y0 + ts - 1
                    for py in range(y_start, y_end, 4):
                        draw.line([(cx, py), (cx, min(py + 1, y_end))],
                                  fill=ROAD_MARK, width=1)

                # EW stripe — dashed horizontal line at tile centre y
                if has_e or has_w:
                    x_start = x0 + 1
                    x_end   = x0 + ts - 1
                    for px in range(x_start, x_end, 4):
                        draw.line([(px, cy), (min(px + 1, x_end), cy)],
                                  fill=ROAD_MARK, width=1)

    def draw_terrain_details(self, tiles: list[list[TerrainType]]) -> None:
        """Draw subtle per-tile texture details over already-painted terrain.

        Call after ``draw_map`` (and ``draw_road_markings`` if used).
        All positions are derived deterministically from (gx, gy) so the
        same map always produces the same texture pattern.
        """
        ts = self.tile_size
        draw = ImageDraw.Draw(self.image)

        for gy, row in enumerate(tiles):
            for gx, tile_type in enumerate(row):
                x0 = self.origin[0] + gx * ts
                y0 = self.origin[1] + gy * ts

                if tile_type is TerrainType.GRASS:
                    # 2–3 small vertical grass tufts per tile, scattered
                    # deterministically by tile position.
                    offsets = [
                        ((gx * 7 + gy * 3) % (ts - 4) + 2,
                         (gx * 3 + gy * 5) % (ts - 4) + 2),
                        ((gx * 11 + gy * 7) % (ts - 4) + 2,
                         (gx * 5 + gy * 11) % (ts - 4) + 2),
                    ]
                    for dx, dy in offsets:
                        draw.line(
                            [(x0 + dx, y0 + dy), (x0 + dx, y0 + dy + 1)],
                            fill=GRASS_TUFT, width=1,
                        )

                elif tile_type is TerrainType.WATER:
                    # 1 short horizontal shimmer line per tile
                    sx = (gx * 5 + gy * 3) % (ts - 6) + 2
                    sy = (gy * 5 + gx * 2) % (ts - 4) + 2
                    draw.line(
                        [(x0 + sx, y0 + sy), (x0 + sx + 3, y0 + sy)],
                        fill=WATER_SHIMMER, width=1,
                    )

                elif tile_type is TerrainType.BEACH:
                    # 3 scattered single-pixel grain dots
                    for i in range(3):
                        bx = (gx * (7 + i * 4) + gy * (3 + i * 2)) % (ts - 2) + 1
                        by = (gy * (5 + i * 3) + gx * (9 + i)) % (ts - 2) + 1
                        draw.point((x0 + bx, y0 + by), fill=BEACH_GRAIN)

                elif tile_type is TerrainType.ROAD:
                    # 2 subtle stud marks at the tile quarter-points
                    draw.point((x0 + ts // 4,     y0 + ts // 2), fill=ROAD_STUD)
                    draw.point((x0 + 3 * ts // 4, y0 + ts // 2), fill=ROAD_STUD)

    # ------------------------------------------------------------------
    # Sprites
    # ------------------------------------------------------------------

    def draw(
        self,
        sprite: IsoSprite,
        gx: float,
        gy: float,
        gz: float = 0,
    ) -> None:
        """Place a sprite with its foot at the centre-bottom of tile (gx, gy).

        The sprite itself retains its iso geometry; only the placement
        anchor is top-down. Positive gz raises the sprite upward by
        ``gz * tile_size`` pixels.
        """
        ts = self.tile_size
        foot_x = self.origin[0] + int((gx + 0.5) * ts)
        foot_y = self.origin[1] + int((gy + 1) * ts) - int(gz * ts)
        sprite.blit(self.image, foot_x, foot_y)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def save(self, path: str, scale: int = 1) -> None:
        """Save canvas to *path* as PNG. *scale* uses nearest-neighbor upscale."""
        img = self.image
        if scale != 1:
            w, h = img.size
            img = img.resize((w * scale, h * scale), Image.NEAREST)
        img.save(path)

    def get_image(self) -> Image.Image:
        return self.image
