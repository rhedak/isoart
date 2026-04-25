"""Unit sprites: Tank, Infantry."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ..palette import AW_INFANTRY_RED, AW_TANK_RED
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
    scale:
        Proportional size multiplier. ``1.0`` renders at 28×22 (the shape
        we tuned against AW references). Values below 1 shrink all
        internal dimensions with a floor that keeps key features visible
        (barrel, turret, treads) — use ~0.6-0.8 for tile-sized map units.
    """

    _BASE_W = 38
    _BASE_H = 26

    def __init__(
        self,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
        scale: float = 1.0,
    ) -> None:
        self.palette = palette if palette is not None else dict(AW_TANK_RED)
        self.scale = max(0.35, scale)
        self._buf: Image.Image | None = None

    # ------------------------------------------------------------------
    # IsoSprite interface
    # ------------------------------------------------------------------

    def get_size(self) -> tuple[int, int]:
        return (
            max(12, int(round(self._BASE_W * self.scale))),
            max(10, int(round(self._BASE_H * self.scale))),
        )

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
        s = self.scale

        # Dimensions (scaled, with per-feature floors so small tanks still
        # show a turret/barrel/treads).
        def _sz(base: int, floor: int) -> int:
            return max(floor, int(round(base * s)))

        body_w   = _sz(22, 12)
        body_d   = _sz(10, 5)
        body_h   = _sz(4, 2)
        turret_w = _sz(10, 5)
        turret_d = _sz(6, 3)
        turret_h = _sz(6, 3)
        tread_h  = _sz(3, 2)
        barrel_len = _sz(11, 6)

        cx = w // 2
        cy = h - 1

        # ---- Treads (dark iso slab at the bottom, slightly wider than body) ----
        tr_fl = (cx - body_w // 2 - 1, cy)
        tr_fr = (cx + body_w // 2 + 1, cy)
        tr_sr = (tr_fr[0] + body_d, tr_fr[1] - body_d // 2)
        tr_fl_t = (tr_fl[0], tr_fl[1] - tread_h)
        tr_fr_t = (tr_fr[0], tr_fr[1] - tread_h)
        tr_sr_t = (tr_sr[0], tr_sr[1] - tread_h)

        # Top face of tread slab — draws first so body occludes the back edge
        tread_top_col = (
            min(255, p["tread"][0] + 40),
            min(255, p["tread"][1] + 40),
            min(255, p["tread"][2] + 40),
            255,
        )
        tr_bl_t = (tr_fl_t[0] + body_d, tr_fl_t[1] - body_d // 2)
        draw.polygon([tr_fl_t, tr_fr_t, tr_sr_t, tr_bl_t], fill=tread_top_col)
        _poly_outline(draw, [tr_fl_t, tr_fr_t, tr_sr_t, tr_bl_t], p["outline"])

        # Front face of tread
        draw.polygon([tr_fl_t, tr_fr_t, tr_fr, tr_fl], fill=p["tread"])
        _poly_outline(draw, [tr_fl_t, tr_fr_t, tr_fr, tr_fl], p["outline"])
        # Side face of tread
        draw.polygon([tr_fr_t, tr_sr_t, tr_sr, tr_fr], fill=p["tread"])
        _poly_outline(draw, [tr_fr_t, tr_sr_t, tr_sr, tr_fr], p["outline"])

        # Tread texture: vertical dashes (1×2 px) along the front face — wheel
        # segments. 1×2 survives the 2× output upscale as readable 2×4 blocks.
        tread_hi = (
            min(255, p["tread"][0] + 60),
            min(255, p["tread"][1] + 60),
            min(255, p["tread"][2] + 60),
            255,
        )
        tread_y_mid = (tr_fl[1] + tr_fl_t[1]) // 2
        dash_step = max(2, int(round(3 * s)))
        for dash_x in range(tr_fl[0] + 2, tr_fr[0] - 1, dash_step):
            draw.line([(dash_x, tread_y_mid), (dash_x, tread_y_mid + 1)], fill=tread_hi, width=1)
        # Top-edge highlight stripe on the tread slab
        tread_top_hi = (
            min(255, p["tread"][0] + 80),
            min(255, p["tread"][1] + 80),
            min(255, p["tread"][2] + 80),
            255,
        )
        draw.line([(tr_fl_t[0] + 1, tr_fl_t[1] + 1), (tr_fr_t[0] - 1, tr_fr_t[1] + 1)],
                  fill=tread_top_hi, width=1)

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
        # Top face — dramatically brighter than front face, dominant surface
        body_top = (
            min(255, p["body_l"][0] + 65),
            min(255, p["body_l"][1] + 65),
            min(255, p["body_l"][2] + 65),
            255,
        )
        draw.polygon([b_fl_t, b_fr_t, b_sr_t, b_bl_t], fill=body_top)
        _poly_outline(draw, [b_fl_t, b_fr_t, b_sr_t, b_bl_t], p["outline"])

        # ---- Turret (box, centered ~40% from front on hull top) ----
        fc_x = (b_fl_t[0] + b_fr_t[0]) // 2
        fc_y = (b_fl_t[1] + b_fr_t[1]) // 2
        bc_x = (b_bl_t[0] + b_sr_t[0]) // 2
        bc_y = (b_bl_t[1] + b_sr_t[1]) // 2
        tcx = fc_x + int((bc_x - fc_x) * 0.65) - body_w // 4
        tcy = fc_y + int((bc_y - fc_y) * 0.65)

        t_fl = (tcx - turret_w // 2, tcy + turret_d // 4)
        t_fr = (tcx + turret_w // 2, tcy + turret_d // 4)
        t_sr = (t_fr[0] + turret_d, t_fr[1] - turret_d // 2)
        t_bl = (t_fl[0] + turret_d, t_fl[1] - turret_d // 2)
        t_fl_t = (t_fl[0], t_fl[1] - turret_h)
        t_fr_t = (t_fr[0], t_fr[1] - turret_h)
        t_sr_t = (t_sr[0], t_sr[1] - turret_h)
        t_bl_t = (t_bl[0], t_bl[1] - turret_h)

        # Front face
        draw.polygon([t_fl_t, t_fr_t, t_fr, t_fl], fill=p["turret"])
        _poly_outline(draw, [t_fl_t, t_fr_t, t_fr, t_fl], p["outline"])
        # Side face (shadow)
        turret_side = (
            max(0, p["turret"][0] - 55),
            max(0, p["turret"][1] - 35),
            max(0, p["turret"][2] - 35),
            255,
        )
        draw.polygon([t_fr_t, t_sr_t, t_sr, t_fr], fill=turret_side)
        _poly_outline(draw, [t_fr_t, t_sr_t, t_sr, t_fr], p["outline"])
        # Top face — very bright to establish the 3D read clearly
        turret_top = (
            min(255, p["turret"][0] + 65),
            min(255, p["turret"][1] + 65),
            min(255, p["turret"][2] + 65),
            255,
        )
        draw.polygon([t_fl_t, t_fr_t, t_sr_t, t_bl_t], fill=turret_top)
        _poly_outline(draw, [t_fl_t, t_fr_t, t_sr_t, t_bl_t], p["outline"])

        # ---- Barrel: from centre of turret right (iso depth) face ----
        barrel_anchor = (
            (t_fr_t[0] + t_sr_t[0]) // 2,
            (t_fr_t[1] + t_sr_t[1]) // 2 + turret_h // 2,
        )
        barrel_tip = (barrel_anchor[0] + barrel_len, barrel_anchor[1] - barrel_len // 3)
        draw.line([barrel_anchor, barrel_tip], fill=p["outline"], width=4)
        draw.line([barrel_anchor, barrel_tip], fill=p["barrel"],  width=2)
        draw.point(barrel_tip, fill=p["outline"])

        self._buf = buf
        return buf


class Infantry(IsoSprite):
    """Isometric pixel-art infantry soldier (AW style).

    Small humanoid: helmeted head, boxy torso, legs, backpack.
    Facing iso-right (same convention as Tank).

    Parameters
    ----------
    palette:
        Color dict with keys: outline, helmet, body, legs, skin, pack.
    scale:
        Size multiplier. ``1.0`` = 14×20 px base. Use ~0.7 for tile-sized
        map units.
    """

    _BASE_W = 14
    _BASE_H = 20

    def __init__(
        self,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
        scale: float = 1.0,
    ) -> None:
        self.palette = palette if palette is not None else dict(AW_INFANTRY_RED)
        self.scale = max(0.5, scale)
        self._buf: Image.Image | None = None

    def get_size(self) -> tuple[int, int]:
        return (
            max(10, int(round(self._BASE_W * self.scale))),
            max(14, int(round(self._BASE_H * self.scale))),
        )

    def get_anchor(self) -> tuple[int, int]:
        w, h = self.get_size()
        return w // 2, h

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        buf = self._render()
        ax, ay = self.get_anchor()
        target.alpha_composite(buf, dest=(x - ax, y - ay))

    def _render(self) -> Image.Image:
        if self._buf is not None:
            return self._buf

        w, h = self.get_size()
        buf = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(buf)
        p = self.palette
        s = self.scale

        def _sz(base: int, floor: int) -> int:
            return max(floor, int(round(base * s)))

        leg_h    = _sz(4, 2)
        leg_w    = _sz(2, 1)
        torso_w  = _sz(5, 3)
        torso_h  = _sz(5, 3)
        head_r   = _sz(3, 2)
        pack_w   = _sz(2, 1)
        pack_h   = _sz(3, 2)

        cx = w // 2
        cy = h - 1

        # ---- Legs (two side-by-side rectangles) ----
        lx = cx - leg_w
        draw.rectangle([lx, cy - leg_h, lx + leg_w - 1, cy], fill=p["legs"])
        draw.rectangle([lx, cy - leg_h, lx + leg_w - 1, cy], outline=p["outline"])
        rx = cx
        draw.rectangle([rx, cy - leg_h, rx + leg_w - 1, cy], fill=p["legs"])
        draw.rectangle([rx, cy - leg_h, rx + leg_w - 1, cy], outline=p["outline"])

        # ---- Backpack (drawn before torso so torso overlaps it) ----
        pack_x = cx + torso_w // 2
        pack_y = cy - leg_h - torso_h
        draw.rectangle(
            [pack_x, pack_y, pack_x + pack_w, pack_y + pack_h],
            fill=p["pack"],
        )
        draw.rectangle(
            [pack_x, pack_y, pack_x + pack_w, pack_y + pack_h],
            outline=p["outline"],
        )

        # ---- Torso (boxy rectangle above legs) ----
        tx = cx - torso_w // 2
        ty = cy - leg_h - torso_h
        draw.rectangle([tx, ty, tx + torso_w, ty + torso_h], fill=p["body"])
        draw.rectangle([tx, ty, tx + torso_w, ty + torso_h], outline=p["outline"])
        # Subtle lit left edge
        body_hi = (
            min(255, p["body"][0] + 40),
            min(255, p["body"][1] + 40),
            min(255, p["body"][2] + 40),
            255,
        )
        draw.line([(tx + 1, ty + 1), (tx + 1, ty + torso_h - 1)], fill=body_hi, width=1)

        # ---- Head (ellipse, skin tone) ----
        hcx = cx
        hcy = ty - head_r
        hbox = [hcx - head_r, hcy - head_r, hcx + head_r, hcy + head_r]
        draw.ellipse(hbox, fill=p["skin"], outline=p["outline"])

        # ---- Helmet (top-half pieslice over the head) ----
        draw.pieslice(hbox, 180, 360, fill=p["helmet"])
        draw.arc(hbox, 180, 360, fill=p["outline"], width=1)

        self._buf = buf
        return buf


class TankLarge(IsoSprite):
    """High-detail isometric tank (AW style), designed from scratch.

    Adds individual elements absent from the compact Tank: hull viewport,
    road wheels on the tread, commander's hatch on the turret top, antenna,
    gun mantlet, and muzzle cap. Same palette keys as Tank.

    Parameters
    ----------
    palette:
        Keys: outline, body_l, body_d, turret, barrel, tread.
    scale:
        1.0 = 50×32 px canvas. Use ~0.65 for AW tile-scale maps.
    """

    _BASE_W = 50
    _BASE_H = 32

    def __init__(
        self,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
        scale: float = 1.0,
    ) -> None:
        self.palette = palette if palette is not None else dict(AW_TANK_RED)
        self.scale = max(0.4, scale)
        self._buf: Image.Image | None = None

    def get_size(self) -> tuple[int, int]:
        return (
            max(16, int(round(self._BASE_W * self.scale))),
            max(12, int(round(self._BASE_H * self.scale))),
        )

    def get_anchor(self) -> tuple[int, int]:
        w, h = self.get_size()
        return w // 2, h

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        buf = self._render()
        ax, ay = self.get_anchor()
        target.alpha_composite(buf, dest=(x - ax, y - ay))

    def _render(self) -> Image.Image:
        if self._buf is not None:
            return self._buf

        w, h = self.get_size()
        buf = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(buf)
        p = self.palette
        s = self.scale

        def _sz(base: int, floor: int) -> int:
            return max(floor, int(round(base * s)))

        body_w    = _sz(28, 14)
        body_d    = _sz(13,  7)
        body_h    = _sz(7,   4)
        turret_w  = _sz(13,  7)
        turret_d  = _sz(8,   4)
        turret_h  = _sz(8,   4)
        tread_h   = _sz(5,   3)
        barrel_len = _sz(16,  9)

        cx = w // 2
        cy = h - 1

        # ---- Tread slab ----
        tr_fl = (cx - body_w // 2 - 1, cy)
        tr_fr = (cx + body_w // 2 + 1, cy)
        tr_sr = (tr_fr[0] + body_d, tr_fr[1] - body_d // 2)
        tr_fl_t = (tr_fl[0], tr_fl[1] - tread_h)
        tr_fr_t = (tr_fr[0], tr_fr[1] - tread_h)
        tr_sr_t = (tr_sr[0], tr_sr[1] - tread_h)
        tr_bl_t = (tr_fl_t[0] + body_d, tr_fl_t[1] - body_d // 2)

        tread_top_col = (
            min(255, p["tread"][0] + 35), min(255, p["tread"][1] + 35),
            min(255, p["tread"][2] + 35), 255,
        )
        tread_hi_col = (
            min(255, p["tread"][0] + 55), min(255, p["tread"][1] + 55),
            min(255, p["tread"][2] + 55), 255,
        )

        # Tread top face (drawn before body so body occludes the back edge)
        draw.polygon([tr_fl_t, tr_fr_t, tr_sr_t, tr_bl_t], fill=tread_top_col)
        _poly_outline(draw, [tr_fl_t, tr_fr_t, tr_sr_t, tr_bl_t], p["outline"])
        # Tread front face
        draw.polygon([tr_fl_t, tr_fr_t, tr_fr, tr_fl], fill=p["tread"])
        _poly_outline(draw, [tr_fl_t, tr_fr_t, tr_fr, tr_fl], p["outline"])
        # Tread side face
        draw.polygon([tr_fr_t, tr_sr_t, tr_sr, tr_fr], fill=p["tread"])
        _poly_outline(draw, [tr_fr_t, tr_sr_t, tr_sr, tr_fr], p["outline"])

        # Road wheels — 3 ellipses evenly spaced across tread front face
        tread_y_mid = (tr_fl[1] + tr_fl_t[1]) // 2
        wheel_rx = max(1, _sz(2, 1))
        wheel_ry = max(1, _sz(2, 1))
        tread_span = tr_fr[0] - tr_fl[0]
        for i in range(3):
            wx = tr_fl[0] + tread_span * (i + 1) // 4
            draw.ellipse(
                [wx - wheel_rx, tread_y_mid - wheel_ry,
                 wx + wheel_rx, tread_y_mid + wheel_ry],
                fill=tread_hi_col,
            )

        # Tread link dashes
        dash_step = max(2, int(round(3 * s)))
        for dx in range(tr_fl[0] + 2, tr_fr[0] - 1, dash_step):
            draw.line([(dx, tread_y_mid), (dx, tread_y_mid + 1)], fill=tread_hi_col, width=1)

        # ---- Hull body ----
        by = cy - tread_h
        b_fl = (cx - body_w // 2, by)
        b_fr = (cx + body_w // 2, by)
        b_sr = (b_fr[0] + body_d, b_fr[1] - body_d // 2)
        b_bl = (b_fl[0] + body_d, b_fl[1] - body_d // 2)
        b_fl_t = (b_fl[0], b_fl[1] - body_h)
        b_fr_t = (b_fr[0], b_fr[1] - body_h)
        b_sr_t = (b_sr[0], b_sr[1] - body_h)
        b_bl_t = (b_bl[0], b_bl[1] - body_h)

        body_top_col = (
            min(255, p["body_l"][0] + 65), min(255, p["body_l"][1] + 65),
            min(255, p["body_l"][2] + 65), 255,
        )

        # Hull front face
        draw.polygon([b_fl_t, b_fr_t, b_fr, b_fl], fill=p["body_l"])
        _poly_outline(draw, [b_fl_t, b_fr_t, b_fr, b_fl], p["outline"])
        # Hull lip: subtle 1 px darker crease at the top edge of the front face
        lip_col = (
            max(0, p["body_l"][0] - 25), max(0, p["body_l"][1] - 25),
            max(0, p["body_l"][2] - 25), 255,
        )
        draw.line([(b_fl_t[0] + 1, b_fl_t[1] + 1), (b_fr_t[0] - 1, b_fr_t[1] + 1)],
                  fill=lip_col, width=1)
        # Viewport: lighter rectangle on hull front face
        vp_cx = (b_fl_t[0] + b_fr_t[0]) // 2 - body_w // 6
        vp_cy = (b_fl_t[1] + b_fl[1]) // 2
        vp_w = max(2, _sz(3, 2))
        vp_h = max(1, _sz(2, 1))
        vp_col = (
            min(255, p["body_l"][0] + 50), min(255, p["body_l"][1] + 50),
            min(255, p["body_l"][2] + 50), 255,
        )
        draw.rectangle([vp_cx, vp_cy - vp_h, vp_cx + vp_w, vp_cy], fill=vp_col)
        draw.rectangle([vp_cx, vp_cy - vp_h, vp_cx + vp_w, vp_cy], outline=p["outline"])

        # Hull side face
        draw.polygon([b_fr_t, b_sr_t, b_sr, b_fr], fill=p["body_d"])
        _poly_outline(draw, [b_fr_t, b_sr_t, b_sr, b_fr], p["outline"])
        # Exhaust port — small dark square on side face
        ex_x = (b_fr[0] + b_sr[0]) // 2 + 1
        ex_y = (b_fr[1] + b_sr[1]) // 2 - 1
        draw.rectangle([ex_x, ex_y, ex_x + 1, ex_y + 1], fill=p["tread"])
        draw.rectangle([ex_x, ex_y, ex_x + 1, ex_y + 1], outline=p["outline"])

        # Hull top face
        draw.polygon([b_fl_t, b_fr_t, b_sr_t, b_bl_t], fill=body_top_col)
        _poly_outline(draw, [b_fl_t, b_fr_t, b_sr_t, b_bl_t], p["outline"])

        # ---- Turret box ----
        # 55% from front to back, offset left so hull top is prominent
        fc_x = (b_fl_t[0] + b_fr_t[0]) // 2
        fc_y = (b_fl_t[1] + b_fr_t[1]) // 2
        bc_x = (b_bl_t[0] + b_sr_t[0]) // 2
        bc_y = (b_bl_t[1] + b_sr_t[1]) // 2
        tcx = fc_x + int((bc_x - fc_x) * 0.55) - body_w // 5
        tcy = fc_y + int((bc_y - fc_y) * 0.55)

        t_fl = (tcx - turret_w // 2, tcy + turret_d // 4)
        t_fr = (tcx + turret_w // 2, tcy + turret_d // 4)
        t_sr = (t_fr[0] + turret_d, t_fr[1] - turret_d // 2)
        t_bl = (t_fl[0] + turret_d, t_fl[1] - turret_d // 2)
        t_fl_t = (t_fl[0], t_fl[1] - turret_h)
        t_fr_t = (t_fr[0], t_fr[1] - turret_h)
        t_sr_t = (t_sr[0], t_sr[1] - turret_h)
        t_bl_t = (t_bl[0], t_bl[1] - turret_h)

        turret_top_col = (
            min(255, p["turret"][0] + 65), min(255, p["turret"][1] + 65),
            min(255, p["turret"][2] + 65), 255,
        )
        turret_side_col = (
            max(0, p["turret"][0] - 55), max(0, p["turret"][1] - 35),
            max(0, p["turret"][2] - 35), 255,
        )
        turret_port_col = (
            min(255, p["turret"][0] + 45), min(255, p["turret"][1] + 45),
            min(255, p["turret"][2] + 45), 255,
        )
        turret_hatch_col = (
            max(0, p["turret"][0] - 60), max(0, p["turret"][1] - 60),
            max(0, p["turret"][2] - 60), 255,
        )

        # Turret front face
        draw.polygon([t_fl_t, t_fr_t, t_fr, t_fl], fill=p["turret"])
        _poly_outline(draw, [t_fl_t, t_fr_t, t_fr, t_fl], p["outline"])
        # Observation port on turret front face
        tp_x = t_fl_t[0] + (t_fr_t[0] - t_fl_t[0]) // 3
        tp_y = (t_fl_t[1] + t_fl[1]) // 2
        draw.rectangle([tp_x, tp_y - 1, tp_x + 1, tp_y], fill=turret_port_col)
        draw.rectangle([tp_x, tp_y - 1, tp_x + 1, tp_y], outline=p["outline"])

        # Turret side face
        draw.polygon([t_fr_t, t_sr_t, t_sr, t_fr], fill=turret_side_col)
        _poly_outline(draw, [t_fr_t, t_sr_t, t_sr, t_fr], p["outline"])

        # Turret top face
        draw.polygon([t_fl_t, t_fr_t, t_sr_t, t_bl_t], fill=turret_top_col)
        _poly_outline(draw, [t_fl_t, t_fr_t, t_sr_t, t_bl_t], p["outline"])
        # Commander's hatch: dark square centered on turret top
        hatch_cx = (t_fl_t[0] + t_sr_t[0]) // 2
        hatch_cy = (t_fl_t[1] + t_sr_t[1]) // 2
        hatch_r = max(1, _sz(2, 1))
        draw.rectangle(
            [hatch_cx - hatch_r, hatch_cy - hatch_r,
             hatch_cx + hatch_r, hatch_cy + hatch_r],
            fill=turret_hatch_col,
        )
        draw.rectangle(
            [hatch_cx - hatch_r, hatch_cy - hatch_r,
             hatch_cx + hatch_r, hatch_cy + hatch_r],
            outline=p["outline"],
        )
        # Antenna — 1 px line at rear corner of turret top
        ant_h = max(3, _sz(5, 3))
        draw.line(
            [(t_bl_t[0] + 1, t_bl_t[1]), (t_bl_t[0] + 1, t_bl_t[1] - ant_h)],
            fill=p["outline"], width=1,
        )

        # ---- Barrel ----
        # Anchor: centre of turret right (depth) face at mid-height
        barrel_anchor = (
            (t_fr_t[0] + t_sr_t[0]) // 2,
            (t_fr_t[1] + t_sr_t[1]) // 2 + turret_h // 2,
        )
        barrel_tip = (barrel_anchor[0] + barrel_len, barrel_anchor[1] - barrel_len // 3)

        # Gun mantlet (dark collar where barrel exits turret)
        collar_w = max(2, _sz(4, 2))
        collar_h = max(3, _sz(5, 3))
        draw.rectangle(
            [barrel_anchor[0] - 1, barrel_anchor[1] - collar_h // 2,
             barrel_anchor[0] + collar_w, barrel_anchor[1] + collar_h // 2],
            fill=p["outline"],
        )
        # Barrel shaft
        draw.line([barrel_anchor, barrel_tip], fill=p["outline"], width=4)
        draw.line([barrel_anchor, barrel_tip], fill=p["barrel"],  width=2)
        # Muzzle cap
        muz_w = max(3, _sz(5, 3))
        muz_h = max(2, _sz(4, 2))
        draw.rectangle(
            [barrel_tip[0] - 1, barrel_tip[1] - muz_h // 2,
             barrel_tip[0] + muz_w, barrel_tip[1] + muz_h // 2],
            fill=p["barrel"],
            outline=p["outline"],
        )

        self._buf = buf
        return buf
