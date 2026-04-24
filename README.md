# isoart

Isometric pixel-art asset library for Python. Draw iso-grid scenes with sprites and export them as PNG images.

![demo](demo.png)

## Install

```bash
pip install isoart
```

Requires Python 3.13+ and depends only on [Pillow](https://python-pillow.org/) and [NumPy](https://numpy.org/).

## Quick start

```python
from isoart import AW_BLUE_PINE, AW_PINE, AW_SNOW_PINE, IsoCanvas, PineTree

COLS, ROWS = 7, 5
TILE_W, TILE_H = 40, 20

canvas_w = (COLS + ROWS) * TILE_W // 2 + 80
canvas_h = (COLS + ROWS) * TILE_H // 2 + 160
origin = (canvas_w // 2, TILE_H * 2)

canvas = IsoCanvas(canvas_w, canvas_h, bg_color=(20, 20, 28, 255),
                   tile_w=TILE_W, tile_h=TILE_H, origin=origin)

canvas.draw_grid(COLS, ROWS)

trees = [
    (PineTree(tier_count=3, tier_size=28, palette=AW_PINE),      2, 1),
    (PineTree(tier_count=3, tier_size=28, palette=AW_BLUE_PINE), 4, 3),
    (PineTree(tier_count=4, tier_size=32, palette=AW_SNOW_PINE), 1, 3),
]

for tree, gx, gy in trees:
    canvas.draw(tree, gx, gy)

canvas.save("demo.png", scale=2)
```

## API

### `IsoCanvas`

The main drawing surface.

```python
IsoCanvas(
    width: int,
    height: int,
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),  # RGBA, default transparent
    tile_w: int = 32,
    tile_h: int = 16,
    origin: tuple[int, int] | None = None,  # defaults to top-center
)
```

| Method | Description |
|--------|-------------|
| `draw_grid(cols, rows)` | Draw a checkerboard diamond-tile grid |
| `draw(sprite, gx, gy, gz=0)` | Place a sprite at grid coordinates |
| `save(path, scale=1)` | Save as PNG, optionally upscaled with nearest-neighbour |
| `get_image()` | Return the underlying `PIL.Image` |

### Sprites

**`PineTree`** — a layered Christmas-tree shaped sprite.

```python
PineTree(
    tier_count: int = 3,   # number of foliage tiers
    tier_size: int = 24,   # pixel width of the widest tier
    palette: dict = AW_PINE,
)
```

### Palettes

Three built-in palettes for `PineTree`:

| Constant | Style |
|----------|-------|
| `AW_PINE` | Classic green pine |
| `AW_BLUE_PINE` | Cold blue-green pine |
| `AW_SNOW_PINE` | Snow-capped pine |

### Transform utilities

```python
from isoart import world_to_screen, screen_to_world, tile_diamond

# Convert grid coords to screen pixels
sx, sy = world_to_screen(gx, gy, gz, tile_w, tile_h)

# Convert screen pixels to grid coords
gx, gy = screen_to_world(sx, sy, tile_w, tile_h)

# Get the four corner vertices of a diamond tile (for polygon drawing)
verts = tile_diamond(gx, gy, tile_w, tile_h, origin)
```

## Development

```bash
uv sync          # install all dependencies including dev
pytest           # run tests
ruff check src   # lint
uv build         # produce wheel + sdist in dist/
```

## License

MIT — see [LICENSE](LICENSE).
