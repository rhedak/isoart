"""Tests for IsoCanvas and TopDownCanvas terrain tile systems."""

from isoart import IsoCanvas, TerrainType, TopDownCanvas


def _center_pixel(canvas: IsoCanvas, gx: int, gy: int) -> tuple[int, int, int, int]:
    """Return the RGBA at the screen-centre of tile (gx, gy)."""
    from isoart import world_to_screen

    sx, sy = world_to_screen(gx, gy, 0, canvas.tile_w, canvas.tile_h)
    px = canvas.origin[0] + sx
    py = canvas.origin[1] + sy
    return canvas.image.getpixel((px, py))


def test_draw_tile_grass_uses_grass_palette():
    c = IsoCanvas(200, 200, tile_w=32, tile_h=16, origin=(100, 100))
    c.draw_tile(TerrainType.GRASS, 0, 0)
    r, g, b, _ = _center_pixel(c, 0, 0)
    # GRASS_LIGHT is (168, 200, 72) — should be close to this (possibly
    # nudged by 1-px rounding at the diamond outline).
    assert g > r and g > b, "Grass should be dominantly green"


def test_draw_tile_water_uses_water_palette():
    c = IsoCanvas(200, 200, tile_w=32, tile_h=16, origin=(100, 100))
    c.draw_tile(TerrainType.WATER, 0, 0)
    r, g, b, _ = _center_pixel(c, 0, 0)
    assert b > r and b > g, "Water should be dominantly blue"


def test_draw_tile_beach_uses_beach_palette():
    c = IsoCanvas(200, 200, tile_w=32, tile_h=16, origin=(100, 100))
    c.draw_tile(TerrainType.BEACH, 0, 0)
    r, g, b, _ = _center_pixel(c, 0, 0)
    # Sand: warm, R >= G > B
    assert r >= g > b, "Beach should be warm sand (R >= G > B)"


def test_draw_tile_road_is_grey():
    c = IsoCanvas(200, 200, tile_w=32, tile_h=16, origin=(100, 100))
    c.draw_tile(TerrainType.ROAD, 0, 0)
    r, g, b, _ = _center_pixel(c, 0, 0)
    # Grey: all three channels within ~5 of each other
    assert max(r, g, b) - min(r, g, b) <= 5, "Road should be neutral grey"


def test_draw_map_paints_every_cell():
    c = IsoCanvas(400, 300, tile_w=32, tile_h=16, origin=(200, 50))
    tiles = [
        [TerrainType.GRASS, TerrainType.BEACH, TerrainType.WATER],
        [TerrainType.ROAD,  TerrainType.GRASS, TerrainType.BEACH],
        [TerrainType.WATER, TerrainType.ROAD,  TerrainType.GRASS],
    ]
    c.draw_map(tiles)
    # Every tile centre should be non-transparent after draw_map.
    for gy in range(3):
        for gx in range(3):
            _, _, _, a = _center_pixel(c, gx, gy)
            assert a == 255, f"Tile ({gx},{gy}) not painted"


def test_draw_map_water_land_border_shows_both_colors():
    c = IsoCanvas(400, 300, tile_w=32, tile_h=16, origin=(200, 50))
    tiles = [[TerrainType.WATER, TerrainType.GRASS]]
    c.draw_map(tiles)
    _, g0, b0, _ = _center_pixel(c, 0, 0)
    r1, g1, b1, _ = _center_pixel(c, 1, 0)
    assert b0 > g0, "Left tile should be blue (water)"
    assert g1 > max(r1, b1), "Right tile should be green (grass)"


# ------------------------------------------------------------------
# TopDownCanvas
# ------------------------------------------------------------------


def _td_center_pixel(c: TopDownCanvas, gx: int, gy: int) -> tuple[int, int, int, int]:
    ts = c.tile_size
    px = c.origin[0] + gx * ts + ts // 2
    py = c.origin[1] + gy * ts + ts // 2
    return c.image.getpixel((px, py))


def test_topdown_draw_tile_grass():
    c = TopDownCanvas(200, 200, tile_size=24, origin=(10, 10))
    c.draw_tile(TerrainType.GRASS, 0, 0)
    r, g, b, _ = _td_center_pixel(c, 0, 0)
    assert g > r and g > b


def test_topdown_draw_tile_water():
    c = TopDownCanvas(200, 200, tile_size=24, origin=(10, 10))
    c.draw_tile(TerrainType.WATER, 0, 0)
    r, g, b, _ = _td_center_pixel(c, 0, 0)
    assert b > r and b > g


def test_topdown_draw_map_paints_every_cell():
    c = TopDownCanvas(400, 300, tile_size=24, origin=(10, 10))
    tiles = [
        [TerrainType.GRASS, TerrainType.BEACH, TerrainType.WATER],
        [TerrainType.ROAD,  TerrainType.GRASS, TerrainType.BEACH],
        [TerrainType.WATER, TerrainType.ROAD,  TerrainType.GRASS],
    ]
    c.draw_map(tiles)
    for gy in range(3):
        for gx in range(3):
            _, _, _, a = _td_center_pixel(c, gx, gy)
            assert a == 255, f"Tile ({gx},{gy}) not painted"


def test_topdown_sprite_anchors_at_tile_center_bottom():
    """A sprite drawn at tile (gx,gy) should place its foot at the tile's
    centre-bottom. We verify via a minimal stub sprite that records the
    foot-position it was blitted at."""
    from isoart.sprites.base import IsoSprite

    class Probe(IsoSprite):
        def __init__(self):
            self.foot = None

        def get_anchor(self):
            return 0, 0

        def get_size(self):
            return 0, 0

        def blit(self, target, x, y):
            self.foot = (x, y)

    c = TopDownCanvas(400, 400, tile_size=20, origin=(30, 40))
    probe = Probe()
    c.draw(probe, 2, 3)
    # Expected: centre-bottom of tile (2,3) = origin + ((2+0.5)*20, (3+1)*20)
    assert probe.foot == (30 + 50, 40 + 80)


def test_topdown_soft_outline_differs_from_hard():
    """Soft outline should be close to the tile fill, not the near-black palette outline."""
    from isoart.palette import GRASS_LIGHT, TILE_OUTLINE

    soft = TopDownCanvas(100, 100, tile_size=20, origin=(10, 10), tile_outline="soft")
    hard = TopDownCanvas(100, 100, tile_size=20, origin=(10, 10), tile_outline="hard")
    soft.draw_tile(TerrainType.GRASS, 0, 0)
    hard.draw_tile(TerrainType.GRASS, 0, 0)

    # Top-left corner of the tile = outline pixel
    soft_px = soft.image.getpixel((10, 10))
    hard_px = hard.image.getpixel((10, 10))

    # Hard outline matches the palette near-black outline
    assert hard_px == TILE_OUTLINE

    # Soft outline is darker than fill but significantly lighter than hard
    assert soft_px != hard_px
    assert soft_px != GRASS_LIGHT  # distinct from fill
    # Soft outline should be closer (in green channel) to the fill than to hard outline
    dist_to_fill = abs(soft_px[1] - GRASS_LIGHT[1])
    dist_to_hard = abs(soft_px[1] - TILE_OUTLINE[1])
    assert dist_to_fill < dist_to_hard


def test_topdown_no_outline():
    """tile_outline=None should leave the border pixel as the fill color."""
    from isoart.palette import GRASS_LIGHT

    c = TopDownCanvas(100, 100, tile_size=20, origin=(10, 10), tile_outline=None)
    c.draw_tile(TerrainType.GRASS, 0, 0)
    # Top-left corner: no outline means pixel is fill color
    assert c.image.getpixel((10, 10)) == GRASS_LIGHT


def test_topdown_sprite_gz_raises():
    from isoart.sprites.base import IsoSprite

    class Probe(IsoSprite):
        def __init__(self):
            self.foot = None

        def get_anchor(self):
            return 0, 0

        def get_size(self):
            return 0, 0

        def blit(self, target, x, y):
            self.foot = (x, y)

    c = TopDownCanvas(400, 400, tile_size=20, origin=(0, 0))
    probe = Probe()
    c.draw(probe, 1, 1, gz=1)
    # gz=1 should lift by tile_size (20 px) upward
    assert probe.foot == (30, 40 - 20)
