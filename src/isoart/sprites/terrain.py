"""Terrain sprites: Mountain, House."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ..palette import AW_HOUSE_NEUTRAL, AW_MOUNTAIN
from .base import IsoSprite


class Mountain(IsoSprite):
    """Isometric mountain — two rounded rocky humps side by side (AW style).

    Each hump is rendered with pieslice-based left/right shading so it reads
    as a 3-D peak rather than a flat blob.

    Parameters
    ----------
    size:
        Pixel width of the larger (front) hump. Overall sprite is ~2× this wide.
    palette:
        Color dict with keys: outline, light, mid, dark, base, base_d.
    """

    def __init__(
        self,
        size: int = 28,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
    ) -> None:
        self.size = size
        self.palette = palette if palette is not None else dict(AW_MOUNTAIN)
        self._buf: Image.Image | None = None

    # ------------------------------------------------------------------
    # IsoSprite interface
    # ------------------------------------------------------------------

    def get_size(self) -> tuple[int, int]:
        s = self.size
        w = s * 2 + 8
        h = int(s * 1.1) + 8
        return w, h

    def get_anchor(self) -> tuple[int, int]:
        w, h = self.get_size()
        return w // 2, h

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        buf = self._render()
        ax, ay = self.get_anchor()
        target.alpha_composite(buf, dest=(x - ax, y - ay))

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self) -> Image.Image:
        if self._buf is not None:
            return self._buf

        w, h = self.get_size()
        buf = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(buf)
        p = self.palette
        s = self.size

        # Back-left hump: smaller, sits slightly higher (behind front hump)
        bx = w // 2 - s // 5
        rw_b = int(s * 0.42)
        rh_b = int(s * 0.58)
        self._draw_hump(draw, p, bx, h - 6, rw_b, rh_b, bright=False)

        # Front-right hump: full size
        fx = w // 2 + s // 5
        rw_f = s // 2
        rh_f = int(s * 0.75)
        self._draw_hump(draw, p, fx, h, rw_f, rh_f, bright=True)

        self._buf = buf
        return buf

    def _draw_hump(
        self,
        draw: ImageDraw.ImageDraw,
        p: dict[str, tuple[int, int, int, int]],
        cx: int,
        base_y: int,
        rw: int,
        rh: int,
        bright: bool,
    ) -> None:
        top_y = base_y - rh
        inner = [cx - rw, top_y, cx + rw, base_y]

        # Outline
        draw.ellipse([cx - rw - 1, top_y - 1, cx + rw + 1, base_y + 1], fill=p["outline"])
        # Base fill (shadow/dark tone for right face)
        draw.ellipse(inner, fill=p["dark"])
        # Left half lit — pieslice 90°→270° (clockwise) = left arc
        lit = p["light"] if bright else p["mid"]
        draw.pieslice(inner, 90, 270, fill=lit)
        # Mid-tone band between lit and shadow — centre strip
        mid_rw = max(2, rw // 5)
        draw.ellipse([cx - mid_rw, top_y + rh // 4, cx + mid_rw, base_y - rh // 6], fill=p["mid"])
        # Highlight near peak
        hl = max(2, rw // 4)
        hx = cx - rw // 3
        hy = top_y + rh // 6
        draw.ellipse([hx - hl, hy, hx + hl, hy + hl * 2], fill=lit)


class House(IsoSprite):
    """Isometric house — box with a pitched roof (AW style).

    Parameters
    ----------
    width:
        Front face width in pixels.
    depth:
        Side face depth in pixels (controls how wide the iso side appears).
    wall_h:
        Height of the walls below the roof.
    roof_h:
        Height of the roof peak above the wall tops.
    palette:
        Color dict with keys: outline, roof_l, roof_r, roof_ridge,
        wall_f, wall_s, window, door.
    """

    def __init__(
        self,
        width: int = 26,
        depth: int = 18,
        wall_h: int = 13,
        roof_h: int = 11,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
    ) -> None:
        self.width = width
        self.depth = depth
        self.wall_h = wall_h
        self.roof_h = roof_h
        self.palette = palette if palette is not None else dict(AW_HOUSE_NEUTRAL)
        self._buf: Image.Image | None = None

    # ------------------------------------------------------------------
    # IsoSprite interface
    # ------------------------------------------------------------------

    def get_size(self) -> tuple[int, int]:
        w = self.width + self.depth + 8
        h = self.wall_h + self.roof_h + self.depth // 2 + 10
        return w, h

    def get_anchor(self) -> tuple[int, int]:
        w, h = self.get_size()
        return w // 2, h

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        buf = self._render()
        ax, ay = self.get_anchor()
        target.alpha_composite(buf, dest=(x - ax, y - ay))

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self) -> Image.Image:
        if self._buf is not None:
            return self._buf

        w, h = self.get_size()
        buf = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(buf)
        p = self.palette

        fw = self.width
        sd = self.depth
        wh = self.wall_h
        rh = self.roof_h

        # Bottom-centre of sprite footprint
        cx = w // 2
        cy = h - 2

        # --- Base vertices (bottom of walls) ---
        front_l = (cx - fw // 2,      cy)
        front_r = (cx + fw // 2,      cy)
        side_r  = (cx + fw // 2 + sd, cy - sd // 2)

        # --- Top of walls ---
        front_l_t = (front_l[0], front_l[1] - wh)
        front_r_t = (front_r[0], front_r[1] - wh)
        side_r_t  = (side_r[0],  side_r[1]  - wh)
        back_l_t  = (cx - fw // 2 + sd, cy - sd // 2 - wh)

        # --- Roof ridge (runs front-to-back along the spine) ---
        ridge_front = (cx + sd // 2,       front_r_t[1] - rh)
        ridge_back  = (cx + sd // 2 + sd // 2, back_l_t[1] - rh)

        # ---- Draw back-to-front ----

        # Side wall (right — darker)
        draw.polygon([front_r_t, side_r_t, side_r, front_r], fill=p["wall_s"])
        _poly_outline(draw, [front_r_t, side_r_t, side_r, front_r], p["outline"])

        # Front wall (left face — lighter)
        draw.polygon([front_l_t, front_r_t, front_r, front_l], fill=p["wall_f"])
        _poly_outline(draw, [front_l_t, front_r_t, front_r, front_l], p["outline"])

        # Window — centred on front wall, upper half
        wmid_x = (front_l_t[0] + front_r_t[0]) // 2
        wmid_y = front_l_t[1] + (wh * 2) // 5
        wsz = max(4, fw // 5)
        draw.rectangle([wmid_x - wsz, wmid_y, wmid_x + wsz, wmid_y + wsz + 1], fill=p["window"])
        draw.rectangle([wmid_x - wsz, wmid_y, wmid_x + wsz, wmid_y + wsz + 1], outline=p["outline"])
        # Window cross-bar
        draw.line([(wmid_x, wmid_y), (wmid_x, wmid_y + wsz + 1)], fill=p["outline"])

        # Door — left of centre on front wall
        dx = front_l[0] + fw // 3
        dw = max(3, fw // 8)
        dh = max(5, wh * 2 // 5)
        draw.rectangle([dx - dw, cy - dh, dx + dw, cy], fill=p["door"])
        draw.rectangle([dx - dw, cy - dh, dx + dw, cy], outline=p["outline"])

        # Roof right face (side — darker)
        draw.polygon([front_r_t, side_r_t, ridge_back, ridge_front], fill=p["roof_r"])
        _poly_outline(draw, [front_r_t, side_r_t, ridge_back, ridge_front], p["outline"])

        # Roof left face (front — lighter)
        draw.polygon([front_l_t, front_r_t, ridge_front], fill=p["roof_l"])
        _poly_outline(draw, [front_l_t, front_r_t, ridge_front], p["outline"])

        # Ridge highlight
        draw.line([ridge_front, ridge_back], fill=p["roof_ridge"], width=2)

        self._buf = buf
        return buf


def _poly_outline(
    draw: ImageDraw.ImageDraw,
    pts: list[tuple[int, int]],
    color: tuple[int, int, int, int],
) -> None:
    n = len(pts)
    for i in range(n):
        draw.line([pts[i], pts[(i + 1) % n]], fill=color, width=1)
