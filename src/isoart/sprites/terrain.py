"""Terrain sprites: Mountain, House."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ..palette import AW_HOUSE_NEUTRAL, AW_MOUNTAIN
from .base import IsoSprite


class Mountain(IsoSprite):
    """Isometric mountain — two pointed peaks side by side (AW style).

    Each peak is a triangular silhouette with left-face lit and right-face
    shadowed to read as a 3-D cone. An optional white cap sits on the tip
    for snow variants (detected by the palette's ``light`` being near-white).

    Parameters
    ----------
    size:
        Pixel width of the larger (front) peak. Overall sprite is ~1.7× this wide.
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
        w = int(s * 1.8) + 8
        h = int(s * 1.0) + 8
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

        # Back-left peak: smaller, sits slightly behind/higher
        bx = w // 2 - int(s * 0.42)
        bw = int(s * 0.55)
        bh = int(s * 0.70)
        self._draw_peak(draw, p, bx, h - 5, bw, bh, bright=False)

        # Front-right peak: full size, in front — wider than tall
        fx = w // 2 + int(s * 0.22)
        fw = int(s * 0.70)
        fh = int(s * 0.90)
        self._draw_peak(draw, p, fx, h - 1, fw, fh, bright=True)

        self._buf = buf
        return buf

    def _draw_peak(
        self,
        draw: ImageDraw.ImageDraw,
        p: dict[str, tuple[int, int, int, int]],
        cx: int,
        base_y: int,
        half_w: int,
        height: int,
        bright: bool,
    ) -> None:
        top_y = base_y - height
        snowy = _is_snowy(p["light"])

        # When snowy, reserve the lightest tone for the cap only so it
        # stands out — the rock body uses darker greys.
        if snowy:
            body_lit    = p["mid"]
            body_shadow = p["dark"]
        elif bright:
            body_lit    = p["light"]
            body_shadow = p["mid"]
        else:
            body_lit    = p["mid"]
            body_shadow = p["dark"]

        peak   = (cx,            top_y)
        base_l = (cx - half_w,   base_y)
        base_r = (cx + half_w,   base_y)
        base_m = (cx,            base_y)

        # Outline — triangle expanded by 1px in every direction
        draw.polygon(
            [(cx, top_y - 1), (cx - half_w - 1, base_y + 1), (cx + half_w + 1, base_y + 1)],
            fill=p["outline"],
        )
        # Left face (lit)
        draw.polygon([peak, base_l, base_m], fill=body_lit)
        # Right face (shadow)
        draw.polygon([peak, base_m, base_r], fill=body_shadow)

        # Rocky base band — darker stripe along the bottom ~20% of the peak
        band_h = max(2, height // 5)
        band_y = base_y - band_h
        band_inset = max(1, band_h // 2)
        band_l = (cx - half_w + band_inset, band_y)
        band_r = (cx + half_w - band_inset, band_y)
        draw.polygon([band_l, base_l, base_m], fill=p["base"])
        draw.polygon([band_r, base_m, base_r], fill=p["base_d"])

        # Snow cap — both peaks get capped on snow variants
        if snowy:
            cap_drop = height // 2
            cap_y = top_y + cap_drop
            cap_hw_at_y = (half_w * cap_drop) // height  # width at cap_y line
            jag = max(1, cap_hw_at_y // 3)
            pts = [
                (cx, top_y),
                (cx + cap_hw_at_y, cap_y),
                (cx + cap_hw_at_y // 2, cap_y - jag),
                (cx,                     cap_y + jag // 2),
                (cx - cap_hw_at_y // 2, cap_y - jag),
                (cx - cap_hw_at_y, cap_y),
            ]
            draw.polygon(pts, fill=p["light"])
        else:
            # Rock-face specks on the lit side — adds texture without randomness
            spec_color = p["dark"]
            step = max(3, height // 5)
            for i in range(1, 4):
                sy = top_y + i * step
                if sy >= base_y - 2:
                    break
                # width of peak at this y, on the lit (left) side
                w_at_y = (half_w * (sy - top_y)) // height
                sx = cx - w_at_y // 2 - i  # stagger
                if sx < cx - w_at_y + 1:
                    continue
                draw.point((sx, sy), fill=spec_color)

        # Single bright pixel at the peak
        draw.point(peak, fill=p["light"])


class House(IsoSprite):
    """Isometric house — chunky cube with a flat capped roof (AW style).

    Tall blocky silhouette with a darker roof slab sitting flush on top
    of the walls and a small window on each visible face. No visible
    door at this scale — AW buildings are viewed from too far away.

    Parameters
    ----------
    width:
        Front face width in pixels.
    depth:
        Side face depth in pixels (controls how wide the iso side appears).
    wall_h:
        Height of the walls below the roof cap.
    roof_h:
        Thickness of the roof cap slab.
    palette:
        Color dict with keys: outline, roof_l, roof_r, roof_ridge,
        wall_f, wall_s, window, door.
    """

    def __init__(
        self,
        width: int = 24,
        depth: int = 18,
        wall_h: int = 20,
        roof_h: int = 5,
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

        cx = w // 2
        cy = h - 2  # bottom-centre of footprint

        # ---- Wall corners (bottom) ----
        front_l = (cx - fw // 2,      cy)
        front_r = (cx + fw // 2,      cy)
        side_r  = (cx + fw // 2 + sd, cy - sd // 2)

        # ---- Wall tops ----
        front_l_t = (front_l[0], front_l[1] - wh)
        front_r_t = (front_r[0], front_r[1] - wh)
        side_r_t  = (side_r[0],  side_r[1]  - wh)
        back_l_t  = (cx - fw // 2 + sd, cy - sd // 2 - wh)

        # ---- Roof slab corners (rh above wall tops) ----
        front_l_r = (front_l_t[0], front_l_t[1] - rh)
        front_r_r = (front_r_t[0], front_r_t[1] - rh)
        side_r_r  = (side_r_t[0],  side_r_t[1]  - rh)
        back_l_r  = (back_l_t[0],  back_l_t[1]  - rh)

        # ---- Draw back-to-front ----

        # Right side wall (darker)
        draw.polygon([front_r_t, side_r_t, side_r, front_r], fill=p["wall_s"])
        _poly_outline(draw, [front_r_t, side_r_t, side_r, front_r], p["outline"])
        # Silhouette rim: 1px lighter edge just inside the back-right vertical
        # edge, so the wall doesn't blend into dark backgrounds.
        wall_rim = _lighten(p["wall_s"], 0.30)
        draw.line(
            [(side_r_t[0] - 1, side_r_t[1] + 1), (side_r[0] - 1, side_r[1])],
            fill=wall_rim, width=1,
        )

        # Front wall (lighter)
        draw.polygon([front_l_t, front_r_t, front_r, front_l], fill=p["wall_f"])
        _poly_outline(draw, [front_l_t, front_r_t, front_r, front_l], p["outline"])

        # ---- Windows: 2×2 grid on front, one iso-skewed window on side ----
        self._draw_front_windows(draw, p, front_l_t, front_r_t, wh, fw)
        self._draw_side_window(draw, p, front_r_t, side_r_t, wh, sd)

        # ---- Roof slab ----
        # Front face of slab (under the top, visible from below-front)
        draw.polygon([front_l_r, front_r_r, front_r_t, front_l_t], fill=p["roof_l"])
        _poly_outline(draw, [front_l_r, front_r_r, front_r_t, front_l_t], p["outline"])
        # Right side of slab
        draw.polygon([front_r_r, side_r_r, side_r_t, front_r_t], fill=p["roof_r"])
        _poly_outline(draw, [front_r_r, side_r_r, side_r_t, front_r_t], p["outline"])
        # Top face of slab (iso-top diamond)
        draw.polygon([front_l_r, front_r_r, side_r_r, back_l_r], fill=p["roof_ridge"])
        _poly_outline(draw, [front_l_r, front_r_r, side_r_r, back_l_r], p["outline"])

        # ---- Silhouette rim: light edge just inside the back-top edges of
        # the roof top. Without this, the dark outline merges into any dark
        # background and the house looks cut off at the back.
        rim = _lighten(p["roof_ridge"], 0.40)
        # Back-right edge (from side_r_r up-left to back_l_r): rim sits 1px
        # below the outline (toward the interior of the top diamond).
        draw.line(
            [(side_r_r[0] - 1, side_r_r[1] + 1), (back_l_r[0], back_l_r[1] + 1)],
            fill=rim, width=1,
        )
        # Back-left edge (from back_l_r down-left to front_l_r): rim sits 1px
        # to the right (toward the interior).
        draw.line(
            [(back_l_r[0] + 1, back_l_r[1] + 1), (front_l_r[0] + 1, front_l_r[1])],
            fill=rim, width=1,
        )

        # ---- Rooftop antenna with small flag ----
        # Place near the back-left of the rooftop diamond
        mast_base_x = (front_l_r[0] + back_l_r[0]) // 2
        mast_base_y = (front_l_r[1] + back_l_r[1]) // 2
        mast_h = max(4, rh + 2)
        mast_top = (mast_base_x, mast_base_y - mast_h)
        draw.line([mast_top, (mast_base_x, mast_base_y)], fill=p["outline"], width=1)
        # Flag — 3×2 rectangle to the right of the mast top
        flag_color = p["roof_l"]
        draw.rectangle(
            [mast_top[0] + 1, mast_top[1], mast_top[0] + 4, mast_top[1] + 2],
            fill=flag_color,
        )
        draw.rectangle(
            [mast_top[0] + 1, mast_top[1], mast_top[0] + 4, mast_top[1] + 2],
            outline=p["outline"],
        )

        self._buf = buf
        return buf

    # ------------------------------------------------------------------
    # Window helpers
    # ------------------------------------------------------------------

    def _draw_front_windows(
        self,
        draw: ImageDraw.ImageDraw,
        p: dict[str, tuple[int, int, int, int]],
        tl: tuple[int, int],
        tr: tuple[int, int],
        wh: int,
        fw: int,
    ) -> None:
        """Draw a symmetric 2×2 grid of square windows on the front wall."""
        wsz = max(3, fw // 8)
        x_mid = (tl[0] + tr[0]) // 2
        gap_x = fw // 4
        # Two rows — upper and lower, evenly spaced inside the wall
        y_up = tl[1] + wh // 4 - wsz // 2
        y_lo = tl[1] + (wh * 3) // 4 - wsz // 2
        for wx in (x_mid - gap_x, x_mid + gap_x):
            for wy in (y_up, y_lo):
                rect = [wx - wsz // 2, wy, wx + wsz // 2, wy + wsz]
                draw.rectangle(rect, fill=p["window"])
                draw.rectangle(rect, outline=p["outline"])

    def _draw_side_window(
        self,
        draw: ImageDraw.ImageDraw,
        p: dict[str, tuple[int, int, int, int]],
        front_r_t: tuple[int, int],
        side_r_t: tuple[int, int],
        wh: int,
        sd: int,
    ) -> None:
        """Draw an iso-skewed square window on the side wall.

        The side wall is a parallelogram: horizontal axis skews upward to the
        right (dx=sd, dy=-sd/2); vertical axis is straight down. We draw the
        window as a parallelogram that inherits the same skew so it reads as
        sitting flat on the wall.
        """
        # Parametric position on the side wall: u along iso-right, v down
        u_c = 0.5   # centre horizontally
        v_c = 0.5   # centre vertically
        size_u = 0.25  # window half-extent along u (fraction of side depth)
        size_v_px = max(3, wh // 4)

        def p_at(u: float, v: float) -> tuple[int, int]:
            x = front_r_t[0] + u * sd
            y = front_r_t[1] + u * (-sd / 2) + v * wh
            return int(x), int(y)

        tl = p_at(u_c - size_u, v_c - size_v_px / (2 * wh))
        tr = p_at(u_c + size_u, v_c - size_v_px / (2 * wh))
        br = p_at(u_c + size_u, v_c + size_v_px / (2 * wh))
        bl = p_at(u_c - size_u, v_c + size_v_px / (2 * wh))

        draw.polygon([tl, tr, br, bl], fill=p["window"])
        _poly_outline(draw, [tl, tr, br, bl], p["outline"])


def _poly_outline(
    draw: ImageDraw.ImageDraw,
    pts: list[tuple[int, int]],
    color: tuple[int, int, int, int],
) -> None:
    n = len(pts)
    for i in range(n):
        draw.line([pts[i], pts[(i + 1) % n]], fill=color, width=1)


def _is_snowy(color: tuple[int, int, int, int]) -> bool:
    """Heuristic: palette's 'light' is near-white → treat as snow variant."""
    r, g, b, _ = color
    return r > 220 and g > 220 and b > 220


def _lighten(
    color: tuple[int, int, int, int],
    amount: float,
) -> tuple[int, int, int, int]:
    """Blend toward white by *amount* ∈ [0, 1]."""
    r, g, b, a = color
    return (
        int(r + (255 - r) * amount),
        int(g + (255 - g) * amount),
        int(b + (255 - b) * amount),
        a,
    )
