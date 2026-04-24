"""Demo: isometric grid with pine trees."""

from isoart import AW_BLUE_PINE, AW_PINE, AW_SNOW_PINE, IsoCanvas, PineTree

COLS, ROWS = 7, 5
TILE_W, TILE_H = 40, 20

# Canvas is wide enough to fit the grid plus tree overhang
canvas_w = (COLS + ROWS) * TILE_W // 2 + 80
canvas_h = (COLS + ROWS) * TILE_H // 2 + 160
origin = (canvas_w // 2, TILE_H * 2)

canvas = IsoCanvas(canvas_w, canvas_h, bg_color=(20, 20, 28, 255),
                   tile_w=TILE_W, tile_h=TILE_H, origin=origin)

canvas.draw_grid(COLS, ROWS)

# Three trees, each with a different palette
trees = [
    (PineTree(tier_count=3, tier_size=28, palette=AW_PINE),       2, 1),
    (PineTree(tier_count=3, tier_size=28, palette=AW_BLUE_PINE),  4, 3),
    (PineTree(tier_count=4, tier_size=32, palette=AW_SNOW_PINE),  1, 3),
]

for tree, gx, gy in trees:
    canvas.draw(tree, gx, gy)

out = "demo.png"
canvas.save(out, scale=2)
print(f"Saved {out}")
