"""Pine tree sprite — the library's style anchor.

Visual design target: Advance Wars 1 pine tree, scaled up.
Each foliage tier is a pointed triangle (Christmas-tree silhouette),
rendered with isometric left/right face shading and a dark outline.
Tiers overlap so the overall shape reads as a layered cone.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from ..palette import AW_PINE
from .base import IsoSprite

# How much of each tier's height the next tier's base overlaps it.
# 0.55 = next tier base starts 55% up the current tier → strong layering.
_TIER_OVERLAP = 0.55

# Width shrink factor per tier step (bottom → top).
_TIER_SHRINK = 0.68

# Tier height as a fraction of its half-width.
# Larger = taller/pointer tiers, ~2.0 gives a sharp Christmas-tree spike.
_TIER_ASPECT = 2.0


class PineTree(IsoSprite):
    """Isometric pixel-art pine tree — Christmas-tree silhouette.

    Parameters
    ----------
    tier_count:
        Number of foliage tiers (2–5). Default 3.
    tier_size:
        Width of the widest (bottom) tier in pixels. Default 30.
    palette:
        Color dict with keys: outline, dark, mid, light, highlight, trunk, trunk_d.
    outline_width:
        Pixel thickness of the dark outline.
    """

    def __init__(
        self,
        tier_count: int = 3,
        tier_size: int = 30,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
        outline_width: int = 1,
    ) -> None:
        self.tier_count = tier_count
        self.tier_size = tier_size
        self.palette = palette if palette is not None else dict(AW_PINE)
        self.outline_width = outline_width
        self._buf: Image.Image | None = None

    # ------------------------------------------------------------------
    # IsoSprite interface
    # ------------------------------------------------------------------

    def get_size(self) -> tuple[int, int]:
        w = self.tier_size + self.outline_width * 4 + 4
        h = self._total_height() + self._trunk_height() + self.outline_width * 2 + 4
        return w, h

    def get_anchor(self) -> tuple[int, int]:
        w, h = self.get_size()
        return w // 2, h

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        buf = self._render()
        ax, ay = self.get_anchor()
        target.alpha_composite(buf, dest=(x - ax, y - ay))

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _trunk_height(self) -> int:
        return max(5, self.tier_size // 5)

    def _trunk_width(self) -> int:
        return max(2, self.tier_size // 10)

    def _tier_half_widths(self) -> list[int]:
        """Half-widths for each tier, index 0 = bottom (widest)."""
        hw = self.tier_size // 2
        return [max(3, int(hw * (_TIER_SHRINK ** i))) for i in range(self.tier_count)]

    def _tier_height(self, half_w: int) -> int:
        return max(5, int(half_w * _TIER_ASPECT))

    def _total_height(self) -> int:
        """Total pixel height occupied by all foliage tiers stacked."""
        hws = self._tier_half_widths()
        heights = [self._tier_height(hw) for hw in hws]
        # First tier contributes full height; each subsequent tier only adds
        # the non-overlapping portion above the previous.
        total = heights[0]
        for h in heights[1:]:
            total += int(h * (1.0 - _TIER_OVERLAP))
        return total

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
        ow = self.outline_width

        cx = w // 2
        trunk_h = self._trunk_height()
        trunk_w = self._trunk_width()

        # --- Foliage tiers, drawn bottom-to-top ---
        # tier_base_y starts above the trunk so the trunk stays visible.
        hws = self._tier_half_widths()
        tier_base_y = h - trunk_h - 1  # bottom tier base sits right above trunk

        for i, half_w in enumerate(hws):
            tier_h = self._tier_height(half_w)
            top_y = tier_base_y - tier_h

            # --- choose shading colors ---
            # Bottom tier is in shadow (darker), top is brightest.
            t = i / max(1, self.tier_count - 1)  # 0.0 at bottom, 1.0 at top
            left_color  = _lerp_color(p["mid"],   p["light"],     t)
            right_color = _lerp_color(p["dark"],  p["mid"],       t)
            hi_color    = _lerp_color(p["light"], p["highlight"], t)

            peak    = (cx,           top_y)
            base_l  = (cx - half_w,  tier_base_y)
            base_r  = (cx + half_w,  tier_base_y)
            base_m  = (cx,           tier_base_y)

            # Outline: draw full triangle expanded by ow in every direction
            draw.polygon(
                [
                    (cx,           top_y      - ow),
                    (cx - half_w - ow, tier_base_y + ow),
                    (cx + half_w + ow, tier_base_y + ow),
                ],
                fill=p["outline"],
            )

            # Left face (facing upper-left = lighter)
            draw.polygon([peak, base_l, base_m], fill=left_color)

            # Right face (facing lower-right = darker)
            draw.polygon([peak, base_m, base_r], fill=right_color)

            # Highlight wedge near peak — upper-left quarter
            if tier_h > 8:
                hi_drop = tier_h // 3
                hi_w    = half_w // 3
                draw.polygon(
                    [
                        peak,
                        (cx - hi_w, top_y + hi_drop),
                        (cx,        top_y + hi_drop),
                    ],
                    fill=hi_color,
                )

            # Single bright pixel at the very peak
            draw.point(peak, fill=p["highlight"])

            # Advance base upward for next tier (overlapping)
            tier_base_y = tier_base_y - int(tier_h * (1.0 - _TIER_OVERLAP))

        # --- Trunk drawn last so it shows in front of the lowest tier base ---
        ty0 = h - trunk_h
        # Dark shadow side (right / bottom edge)
        draw.rectangle([cx - trunk_w,     ty0,     cx + trunk_w + 1, h],     fill=p["trunk_d"])
        # Lighter face
        draw.rectangle([cx - trunk_w,     ty0,     cx + trunk_w,     h - 1], fill=p["trunk"])
        # Bright left highlight strip
        draw.rectangle([cx - trunk_w,     ty0 + 1, cx - trunk_w + 1, h - 1], fill=p["trunk"])

        self._buf = buf
        return buf


class RoundTree(IsoSprite):
    """Isometric deciduous tree — single ovoid blob (AW forest style).

    One crown-shaped ellipse with pieslice-based left/right shading so
    the foliage reads as a 3-D dome rather than a flat disc.

    Parameters
    ----------
    tier_count:
        Kept for API compatibility; currently unused.
    tier_size:
        Pixel width of the crown. Default 28.
    palette:
        Color dict with keys: outline, dark, mid, light, highlight, trunk, trunk_d.
    """

    _ASPECT = 1.10  # crown height as fraction of width — slightly taller than wide

    def __init__(
        self,
        tier_count: int = 3,
        tier_size: int = 28,
        palette: dict[str, tuple[int, int, int, int]] | None = None,
    ) -> None:
        from ..palette import AW_ROUND_TREE
        self.tier_count = tier_count
        self.tier_size = tier_size
        self.palette = palette if palette is not None else dict(AW_ROUND_TREE)
        self._buf: Image.Image | None = None

    def get_size(self) -> tuple[int, int]:
        crown_h = int(self.tier_size * self._ASPECT)
        w = self.tier_size + 8
        h = crown_h + self._trunk_height() + 6
        return w, h

    def get_anchor(self) -> tuple[int, int]:
        w, h = self.get_size()
        return w // 2, h

    def blit(self, target: Image.Image, x: int, y: int) -> None:
        buf = self._render()
        ax, ay = self.get_anchor()
        target.alpha_composite(buf, dest=(x - ax, y - ay))

    def _trunk_height(self) -> int:
        return max(5, self.tier_size // 5)

    def _trunk_width(self) -> int:
        return max(2, self.tier_size // 8)

    def _render(self) -> Image.Image:
        if self._buf is not None:
            return self._buf

        w, h = self.get_size()
        buf = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(buf)
        p = self.palette

        cx = w // 2
        trunk_h = self._trunk_height()
        trunk_w = self._trunk_width()
        crown_h = int(self.tier_size * self._ASPECT)
        half_w  = self.tier_size // 2

        base_y = h - trunk_h

        # --- Crown: two stacked ellipses tuned so the silhouette tapers
        # smoothly from wide base to narrow top, without a waist notch.
        # Tuning: at the upper ellipse's equator the two widths match
        # (~0.5·half_w), giving a smooth crossover.
        lo_hw = half_w
        lo_h  = int(crown_h * 0.80)
        lo_cy = base_y - int(crown_h * 0.40)
        lo_outer = [cx - lo_hw - 1, lo_cy - lo_h // 2 - 1, cx + lo_hw + 1, lo_cy + lo_h // 2 + 1]
        lo_inner = [cx - lo_hw,     lo_cy - lo_h // 2,     cx + lo_hw,     lo_cy + lo_h // 2]

        up_hw = max(3, int(half_w * 0.55))
        up_h  = int(crown_h * 0.50)
        up_cy = base_y - int(crown_h * 0.75)
        up_outer = [cx - up_hw - 1, up_cy - up_h // 2 - 1, cx + up_hw + 1, up_cy + up_h // 2 + 1]
        up_inner = [cx - up_hw,     up_cy - up_h // 2,     cx + up_hw,     up_cy + up_h // 2]

        # Outlines first (lower then upper, so upper's outline trims any
        # stray lower outline at the waist)
        draw.ellipse(lo_outer, fill=p["outline"])
        draw.ellipse(up_outer, fill=p["outline"])

        # Shadow base fills
        draw.ellipse(lo_inner, fill=p["dark"])
        draw.ellipse(up_inner, fill=p["dark"])

        # Left-half lit on both
        draw.pieslice(lo_inner, 90, 270, fill=p["mid"])
        draw.pieslice(up_inner, 90, 270, fill=p["mid"])

        # Soft top-left rim of lighter tone — only on the upper ellipse
        # (that's the visually "top" part of the teardrop)
        rim_inset = max(1, up_hw // 5)
        rim_box = [
            cx - up_hw + rim_inset,
            up_cy - up_h // 2 + rim_inset,
            cx + up_hw - rim_inset,
            up_cy + up_h // 2 - rim_inset,
        ]
        draw.pieslice(rim_box, 180, 300, fill=p["light"])

        # Highlight blob near top-left of the upper ellipse
        hl = max(2, up_hw // 4)
        hx = cx - up_hw // 3
        hy = up_cy - up_h // 4
        draw.ellipse([hx - hl, hy, hx + hl, hy + hl * 2], fill=p["highlight"])

        # --- Trunk ---
        ty0 = h - trunk_h
        draw.rectangle([cx - trunk_w,     ty0,     cx + trunk_w + 1, h],     fill=p["trunk_d"])
        draw.rectangle([cx - trunk_w,     ty0,     cx + trunk_w,     h - 1], fill=p["trunk"])

        self._buf = buf
        return buf


def _lerp_color(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
    t: float,
) -> tuple[int, int, int, int]:
    """Linear interpolate between two RGBA colors."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))  # type: ignore[return-value]
