"""IsoCanvas — the main drawing surface."""

from __future__ import annotations

from enum import Enum

from PIL import Image, ImageDraw

from .palette import (
    BEACH_DARK,
    BEACH_LIGHT,
    BEACH_OUTLINE,
    GRASS_DARK,
    GRASS_LIGHT,
    ROAD_DARK,
    ROAD_LIGHT,
    ROAD_OUTLINE,
    TILE_OUTLINE,
    WATER_DARK,
    WATER_LIGHT,
    WATER_OUTLINE,
)
from .sprites.base import IsoSprite
from .transform import tile_diamond, world_to_screen


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
