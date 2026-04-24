"""Unit sprites: Tank."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ..palette import AW_TANK_RED
from .base import IsoSprite
from .terrain import _poly_outline


class Tank(IsoSprite):
    """Isometric pixel-art tank (AW style).

    Chunky tread-platform + boxy body + turret cube + stubby barrel,
    facing "forward" (iso +gx direction, screen lower-right).

    Parameters
    ----------
    palette:
        Color dict with keys: outline, body_l, body_d, turret, barrel, tread.
    """

    def __init__(
        self,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
    ) -> None:
        self.palette = palette if palette is not None else dict(AW_TANK_RED)
        self._buf: Image.Image | None = None

    # ------------------------------------------------------------------
    # IsoSprite interface
    # ------------------------------------------------------------------

    def get_size(self) -> tuple[int, int]:
        return 28, 22

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

        # Dimensions
        body_w, body_d, body_h = 16, 9, 6
        turret_w, turret_d, turret_h = 9, 5, 4
        tread_h = 3
        barrel_len = 8

        cx = w // 2
        cy = h - 1

        # ---- Treads (dark iso slab at the bottom, slightly wider than body) ----
        tr_fl = (cx - body_w // 2 - 1, cy)
        tr_fr = (cx + body_w // 2 + 1, cy)
        tr_sr = (tr_fr[0] + body_d, tr_fr[1] - body_d // 2)
        tr_bl = (tr_fl[0] + body_d, tr_fl[1] - body_d // 2)
        tr_fl_t = (tr_fl[0], tr_fl[1] - tread_h)
        tr_fr_t = (tr_fr[0], tr_fr[1] - tread_h)
        tr_sr_t = (tr_sr[0], tr_sr[1] - tread_h)
        tr_bl_t = (tr_bl[0], tr_bl[1] - tread_h)

        # Front face of tread
        draw.polygon([tr_fl_t, tr_fr_t, tr_fr, tr_fl], fill=p["tread"])
        _poly_outline(draw, [tr_fl_t, tr_fr_t, tr_fr, tr_fl], p["outline"])
        # Side face of tread
        draw.polygon([tr_fr_t, tr_sr_t, tr_sr, tr_fr], fill=p["tread"])
        _poly_outline(draw, [tr_fr_t, tr_sr_t, tr_sr, tr_fr], p["outline"])

        # Tread texture: small dashes along the front-bottom edge (wheel hint)
        tread_hi = (
            min(255, p["tread"][0] + 40),
            min(255, p["tread"][1] + 40),
            min(255, p["tread"][2] + 40),
            255,
        )
        tread_y_mid = (tr_fl[1] + tr_fl_t[1]) // 2
        for dash_x in range(tr_fl[0] + 2, tr_fr[0] - 1, 3):
            draw.point((dash_x, tread_y_mid), fill=tread_hi)

        # ---- Body (iso box sitting on treads) ----
        by = cy - tread_h
        b_fl = (cx - body_w // 2, by)
        b_fr = (cx + body_w // 2, by)
        b_sr = (b_fr[0] + body_d, b_fr[1] - body_d // 2)
        b_bl = (b_fl[0] + body_d, b_fl[1] - body_d // 2)
        b_fl_t = (b_fl[0], b_fl[1] - body_h)
        b_fr_t = (b_fr[0], b_fr[1] - body_h)
        b_sr_t = (b_sr[0], b_sr[1] - body_h)
        b_bl_t = (b_bl[0], b_bl[1] - body_h)

        # Front face (lit)
        draw.polygon([b_fl_t, b_fr_t, b_fr, b_fl], fill=p["body_l"])
        _poly_outline(draw, [b_fl_t, b_fr_t, b_fr, b_fl], p["outline"])
        # Side face (shadow)
        draw.polygon([b_fr_t, b_sr_t, b_sr, b_fr], fill=p["body_d"])
        _poly_outline(draw, [b_fr_t, b_sr_t, b_sr, b_fr], p["outline"])
        # Top face
        draw.polygon([b_fl_t, b_fr_t, b_sr_t, b_bl_t], fill=p["body_l"])
        _poly_outline(draw, [b_fl_t, b_fr_t, b_sr_t, b_bl_t], p["outline"])

        # ---- Turret (smaller iso box centered on body top) ----
        # Centre of body top face (iso diamond centroid)
        tcx = (b_fl_t[0] + b_sr_t[0]) // 2
        tcy = (b_fl_t[1] + b_sr_t[1]) // 2
        t_fl = (tcx - turret_w // 2,     tcy + turret_d // 4)
        t_fr = (tcx + turret_w // 2,     tcy + turret_d // 4)
        t_sr = (t_fr[0] + turret_d, t_fr[1] - turret_d // 2)
        t_bl = (t_fl[0] + turret_d, t_fl[1] - turret_d // 2)
        t_fl_t = (t_fl[0], t_fl[1] - turret_h)
        t_fr_t = (t_fr[0], t_fr[1] - turret_h)
        t_sr_t = (t_sr[0], t_sr[1] - turret_h)
        t_bl_t = (t_bl[0], t_bl[1] - turret_h)

        # Turret front face — lighter than body so the turret pops.
        draw.polygon([t_fl_t, t_fr_t, t_fr, t_fl], fill=p["turret"])
        _poly_outline(draw, [t_fl_t, t_fr_t, t_fr, t_fl], p["outline"])
        # Turret right side — darker shadow
        turret_shadow = (
            max(0, p["turret"][0] - 60),
            max(0, p["turret"][1] - 30),
            max(0, p["turret"][2] - 30),
            255,
        )
        draw.polygon([t_fr_t, t_sr_t, t_sr, t_fr], fill=turret_shadow)
        _poly_outline(draw, [t_fr_t, t_sr_t, t_sr, t_fr], p["outline"])
        # Turret top — use turret color (slightly lighter than body) so it
        # reads as a raised cap, not a pit.
        draw.polygon([t_fl_t, t_fr_t, t_sr_t, t_bl_t], fill=p["turret"])
        _poly_outline(draw, [t_fl_t, t_fr_t, t_sr_t, t_bl_t], p["outline"])

        # ---- Barrel: thick dark line emerging from the turret's right-front ----
        barrel_anchor = (
            (t_fr_t[0] + t_sr_t[0]) // 2,
            (t_fr_t[1] + t_sr_t[1]) // 2 + 1,
        )
        barrel_tip = (barrel_anchor[0] + barrel_len, barrel_anchor[1] + barrel_len // 3)
        # Outline (wider)
        draw.line([barrel_anchor, barrel_tip], fill=p["outline"], width=3)
        # Barrel body
        draw.line([barrel_anchor, barrel_tip], fill=p["barrel"], width=1)
        # Muzzle tip dot
        draw.point(barrel_tip, fill=p["outline"])

        self._buf = buf
        return buf
