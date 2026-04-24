"""Tests for unit sprites."""

from PIL import Image

from isoart import AW_TANK_BLUE, AW_TANK_RED, Tank


def _render(sprite) -> Image.Image:
    w, h = sprite.get_size()
    buf = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ax, ay = sprite.get_anchor()
    sprite.blit(buf, ax + 2, ay + 2)
    return buf


def _non_transparent(img: Image.Image) -> int:
    return sum(1 for v in img.getchannel("A").tobytes() if v > 0)


def test_tank_default_renders_pixels():
    t = Tank()
    assert _non_transparent(_render(t)) > 30


def test_tank_red_and_blue_both_render():
    for palette in (AW_TANK_RED, AW_TANK_BLUE):
        t = Tank(palette=palette)
        assert _non_transparent(_render(t)) > 30


def test_tank_anchor_within_bounds():
    t = Tank()
    w, h = t.get_size()
    ax, ay = t.get_anchor()
    assert 0 <= ax <= w
    assert 0 <= ay <= h


def test_tank_red_and_blue_differ():
    """Rendered red and blue tanks should produce different pixels."""
    r = _render(Tank(palette=AW_TANK_RED))
    b = _render(Tank(palette=AW_TANK_BLUE))
    assert r.tobytes() != b.tobytes()
