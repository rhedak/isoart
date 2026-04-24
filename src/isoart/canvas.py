"""IsoCanvas — the main drawing surface."""

from __future__ import annotations

from PIL import Image, ImageDraw

from .palette import GRASS_DARK, GRASS_LIGHT, TILE_OUTLINE
from .sprites.base import IsoSprite
from .transform import tile_diamond, world_to_screen


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
