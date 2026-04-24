"""Tests for isometric coordinate transforms."""

from isoart import screen_to_world, world_to_screen


def test_origin():
    assert world_to_screen(0, 0) == (0, 0)


def test_x_axis():
    sx, sy = world_to_screen(1, 0)
    assert sx > 0
    assert sy > 0


def test_y_axis():
    sx, sy = world_to_screen(0, 1)
    assert sx < 0
    assert sy > 0


def test_z_raises():
    _, sy0 = world_to_screen(2, 2, gz=0)
    _, sy1 = world_to_screen(2, 2, gz=1)
    assert sy1 < sy0  # higher gz → higher on screen (lower sy)


def test_round_trip():
    for gx, gy in [(0, 0), (3, 2), (1, 5)]:
        sx, sy = world_to_screen(gx, gy)
        gx2, gy2 = screen_to_world(sx, sy)
        assert abs(gx2 - gx) < 1e-9
        assert abs(gy2 - gy) < 1e-9


def test_diamond_symmetry():
    from isoart import tile_diamond
    verts = tile_diamond(0, 0)
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    assert xs[0] == xs[2]        # top and bottom share x
    assert xs[1] == -xs[3]       # left and right are symmetric
    assert ys[1] == ys[3]        # left and right share y
