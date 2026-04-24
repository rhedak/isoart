# Roadmap — AW Dogfights PoC

Live progress document for the PoC that replicates `references/AW_Dogfights_Map.png` using only generated assets. Updated after every change.

## Current status

**Phase:** Phase 1 + 1.5 done. Ready for Phase 2 (Tank sprite).
**Last update:** 2026-04-24
**Last commit:** pending — Phase 1.5 commit
**Sample scorecard:** 12/12 PASS (pines, round trees, mountains, houses). `terrain_preview.png` (iso) + `topdown_preview.png` (square) added.
**Tests:** 22/22 passing. Ruff clean.

## Scope (locked)

- **Fidelity:** AW-inspired scene in iso, not pixel-perfect replica of the GBA top-down image.
- **Units:** one type (Tank), two faction palettes (red, blue), 3–4 per side.
- **New tiles:** water, beach, road (single generic road, non-directional).
- **Stack:** Pillow only. Matplotlib evaluated and deliberately skipped.

## Phases

### Phase 1 — Terrain tile system ✅
- [x] Add `TerrainType` enum (`GRASS`, `WATER`, `BEACH`, `ROAD`) in `src/isoart/canvas.py`
- [x] Add tile color palettes (`WATER_*`, `BEACH_*`, `ROAD_*`) in `src/isoart/palette.py`
- [x] Implement `IsoCanvas.draw_tile(tile_type, gx, gy)`
- [x] Implement `IsoCanvas.draw_map(tiles: list[list[TerrainType]])`
- [x] Keep `draw_grid` backward-compatible (don't break demos)
- [x] Export `TerrainType` from `src/isoart/__init__.py`
- [x] Unit test: `tests/test_canvas.py` — 6 tests covering per-tile colors + map painting + border

### Phase 1.5 — Top-down terrain canvas ✅

**Rationale:** the AW reference draws terrain as top-down square tiles while keeping iso perspective for units/buildings/trees. Our current `IsoCanvas` draws terrain as iso diamonds — that reads as a puzzle board, not a battle map. To match the AW vibe we need top-down terrain with iso sprites layered on top.

**Design choice:** new `TopDownCanvas` class (not a mode flag on `IsoCanvas`). Keeps both rendering styles available, makes intent obvious in user code.

**Transform math:**
- Terrain tile at (gx, gy) → square at screen `(origin.x + gx*ts, origin.y + gy*ts)` of side `ts` (tile_size).
- Sprite placed at (gx, gy) → iso foot anchor at tile's **visual center-bottom**: `(origin.x + (gx+0.5)*ts, origin.y + (gy+1)*ts)`. Sprite itself still renders with its existing iso geometry (no sprite changes needed).
- Z raises sprite by `gz * ts` as before.

**Files:**
- [x] `src/isoart/canvas.py` — `TopDownCanvas` class with `draw_map` / `draw_tile` / `draw` / `save` / `get_image`. Square tiles via `draw.rectangle`. Sprite anchor = tile centre-bottom; `gz * tile_size` lifts.
- [x] Export `TopDownCanvas` from `src/isoart/__init__.py`.
- [x] `samples/generate.py` — `topdown_preview.png` shows the AW-style square-tile version alongside the iso `terrain_preview.png`. Map layout shared between both via a small legend helper.
- [x] `tests/test_canvas.py` — 5 new tests: per-tile colors (grass, water), full map painting, sprite anchor math, `gz` lifting.

**Out of scope for Phase 1.5 (park for Phase 3):**
- Whether Phase 3 scene composition uses `TopDownCanvas` (likely yes, given the reference).
- Multi-tile-size support (for now, `tile_size` is a single integer; both w and h).

### Phase 2 — Tank sprite + faction palettes
- [ ] Add `AW_TANK_RED`, `AW_TANK_BLUE` in `src/isoart/palette.py`
- [ ] Create `src/isoart/sprites/units.py` with `Tank(IsoSprite)`
- [ ] Export `Tank` from `src/isoart/sprites/__init__.py` and `src/isoart/__init__.py`
- [ ] Add `tank_red`, `tank_blue` to `samples/generate.py`
- [ ] Iterate on Tank silhouette (PASS/FAIL loop, up to 3 passes)
- [ ] Unit test: `tests/test_units.py` — render Tank with both palettes

### Phase 3 — Scene composition
- [ ] Create `examples/aw_dogfights.py`
- [ ] Define ~22×14 tile grid (grass-left / water-middle / grass-right + beach borders + road)
- [ ] Place mountains along the reference's mountain lines
- [ ] Scatter pine + round trees across both land masses
- [ ] Cluster red houses on left, blue houses on right (as "bases")
- [ ] Place 3–4 red tanks near red base, 3–4 blue tanks near blue base
- [ ] Draw order: terrain → sprites back-to-front by `gy`
- [ ] Save `aw_dogfights.png` at scale 3–4

### Phase 4 — Docs + polish
- [ ] Update README: add `Tank`, `AW_TANK_RED/BLUE`, `TerrainType`, `draw_map` docs
- [ ] Embed `aw_dogfights.png` in README under a "Demo" section
- [ ] Update sample scorecard in this roadmap to include Tank variants
- [ ] Verify: `uv run pytest -q` green, `uv run ruff check` clean
- [ ] Verify: visual side-by-side of `aw_dogfights.png` vs. `references/AW_Dogfights_Map.png`

## Sample scorecard

| Sprite | Status | Iterations |
|---|---|---|
| `pine_green` | PASS | 1 |
| `pine_blue` | PASS | 1 |
| `pine_snow` | PASS | 1 |
| `pine_tall` | PASS | 1 |
| `round_green` | PASS | 2 (+ polish) |
| `round_autumn` | PASS | 2 (+ polish) |
| `round_blue` | PASS | 2 (+ polish) |
| `mountain` | PASS | 2 (+ polish) |
| `mountain_snow` | PASS | 2 (+ polish) |
| `house_red` | PASS | 1 (+ polish ×2) |
| `house_blue` | PASS | 1 (+ polish ×2) |
| `house_neutral` | PASS | 1 (+ polish ×2) |
| `tank_red` | — | — |
| `tank_blue` | — | — |

## Decisions log

- **2026-04-24** — Picked iso-inspired (not pixel-perfect) scope. Stay in iso projection.
- **2026-04-24** — One unit type (Tank); two faction palettes.
- **2026-04-24** — Three tile types: water, beach, road. Road is single non-directional variant for PoC.
- **2026-04-24** — Pillow-only. Matplotlib rejected for this PoC (anti-aliasing fights pixel-art aesthetic; unnecessary dep).
- **2026-04-24** — `aw_dogfights.png` will be committed to the repo so the README can embed it without a build step.
- **2026-04-24** — Commit after every step; roadmap updated in each commit.
- **2026-04-24** — AW terrain is top-down squares + iso sprites, not full-iso. Adding `TopDownCanvas` as a new class (Phase 1.5) rather than a mode flag. PoC scene will use top-down terrain.

## Open questions / follow-ups

- After PoC passes, revisit: directional road tiles (NS/EW/corners), multi-tile bases (HQs, factories), more unit types (infantry, artillery, plane).

## Risks / non-goals

- Iso vs GBA top-down is a projection gap. Output is "AW in iso," not a pixel replica.
- Unit density lower than reference (3–4 vs. 20+) — enough to read as "factions present."
- No multi-tile structures; bases are clusters of single-tile houses.
- Roads are blocky at corners (non-directional).
