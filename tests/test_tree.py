"""Tests for PineTree sprite rendering."""

from PIL import Image
from isoart import AW_BLUE_PINE, AW_PINE, AW_SNOW_PINE, PineTree


def _render(tree: PineTree) -> Image.Image:
    w, h = tree.get_size()
    buf = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ax, ay = tree.get_anchor()
    tree.blit(buf, ax + 2, ay + 2)
    return buf


def test_default_tree_has_pixels():
    tree = PineTree()
    img = _render(tree)
    non_transparent = sum(1 for p in img.getdata() if p[3] > 0)
    assert non_transparent > 10, "Tree should draw visible pixels"


def test_tree_size_scales_with_tier_size():
    small = PineTree(tier_size=16)
    large = PineTree(tier_size=40)
    sw, sh = small.get_size()
    lw, lh = large.get_size()
    assert lw > sw
    assert lh > sh


def test_all_palettes_render():
    for palette in [AW_PINE, AW_BLUE_PINE, AW_SNOW_PINE]:
        tree = PineTree(palette=palette)
        img = _render(tree)
        non_transparent = sum(1 for p in img.getdata() if p[3] > 0)
        assert non_transparent > 10


def test_tier_counts():
    for n in [2, 3, 4]:
        tree = PineTree(tier_count=n)
        img = _render(tree)
        non_transparent = sum(1 for p in img.getdata() if p[3] > 0)
        assert non_transparent > 10


def test_anchor_within_bounds():
    tree = PineTree()
    w, h = tree.get_size()
    ax, ay = tree.get_anchor()
    assert 0 <= ax <= w
    assert 0 <= ay <= h
