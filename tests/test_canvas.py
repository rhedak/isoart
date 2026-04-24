"""Tests for IsoCanvas terrain tile system."""

from isoart import IsoCanvas, TerrainType


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
