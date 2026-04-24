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


def test_tank_default_scale_unchanged():
    """scale=1.0 default must preserve the 28x22 sprite size."""
    assert Tank().get_size() == (28, 22)


def test_tank_scale_shrinks_size():
    big = Tank().get_size()
    small = Tank(scale=0.6).get_size()
    assert small[0] < big[0]
    assert small[1] < big[1]


def test_tank_scaled_still_renders():
    t = Tank(scale=0.6)
    assert _non_transparent(_render(t)) > 20


def test_tank_scale_floor_prevents_degenerate_size():
    """Very small scale should still produce a readable sprite (not 0x0)."""
    t = Tank(scale=0.1)  # will be floored internally
    w, h = t.get_size()
    assert w >= 12 and h >= 10
    assert _non_transparent(_render(t)) > 10
