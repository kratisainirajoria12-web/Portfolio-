# Krati — "The Seed" portfolio: handoff notes

Krati is a product designer. This is her scroll-driven portfolio site. Her 3D caricature catches a sunflower seed and plants it. The camera follows the seed underground, where it roots, then rises with the sprout as it grows into a sunflower. One seed falls back to her and the page loops.

**Working style she expects:**
- She gives feedback point by point, often in Hinglish. When she says "do not start until I tell you", wait.
- Change only what she asks for. She has rejected unasked-for restyles more than once.
- She prefers to see results, not explanations.

## Run it
`npx serve .` (or `python3 -m http.server`) in this folder, then open `index.html`. It must be served from a local server; opening the file directly won't work.

## Files
| File / folder | What it is |
|---|---|
| `index.html` | Page, CSS, panels/text, and an **inlined copy** of `macro.js` + `main.js` |
| `main.js` | Timeline, frame loader, 2D shot renderer, colour grading, text motion, scroll damping, loop |
| `macro.js` | three.js seed head: phyllotaxis seeds, push-in, gold bokeh, dark veil, single falling seed |
| `vendor/three.min.js` | three r160. The page loads the same build from jsDelivr |
| `catch/` | Krati catches and plants the seed. 109 frames, 1280x720 webp |
| `dive/` | Krati's own soil-dive video. Sheets of 4 frames stacked vertically (`s000.webp`…), 151 frames |
| `grow/` | Underground: seed cracks and roots. 120 frames |
| `bloom/` | Sprout to full bloom. 280 files: E239–261 (0–22), then a 160-frame sprout bridge (23–182, made by `tools/bridge.py`), then E315–440 (183–279). The disc is recoloured brown. `bloomIdx()` in main.js maps the story frame (old 0–159 scale) to a file |
| `hold/` | 8 s seamless "living photograph" loop for the sunflower pause. Sheets of 4, 96 frames, played at 12 fps |
| `zoom/` | Push into the flower head. 22 frames |
| `tools/` | Python/OpenCV scripts that generated the derived frames (paths inside point to the old scratch folder) |
| `SEED-keyframes.txt` | Motion data extracted from theseed.volm.studio, the reference for the motion feel |

**After editing `main.js` or `macro.js`, re-inline them into `index.html`.** The script tag holds `macro.js`, a newline, then `main.js`.

## Timeline (`TL` in main.js, units = vh of story)
- `catch 10–200`
- `dive 185–262`: this stretch gets extra scroll; scroll space ≠ story space (see `S2U`/`U2S`)
- `roots 262–410`
- `bloom 410–1110`
- `hold 1110–1330`: pause with the breeze loop. The camera only drifts here (no zoom, no roll)
- `zoom 1330–1440`
- `macro 1440–1600`: 3D seed head ripens, camera pushes in
- `drop 1590–1745`: screen darkens to black, one seed stays lit and falls
- `fall 1630–1800`: the seed falls out of frame, then Krati's meadow fades up from black
- `end 1800–1830`: seamless jump back to the top
- Panel `data-a`/`data-b` values are in the same story units

## Decisions she made (don't undo without asking)
- Keep the "v1" style. She rejected a full SEED-site restyle and a cartoonish 3D growth.
- Soil dive: her video, ending on the upright seed in the soil, then a straight cut to the roots clip. She removed both the morph transition and the black-fade transition.
- Sprout (Day ~19–28): a slim sprout with a closed pointed bud pushes out of the cracked seed (her reference image), the camera tilts up with it, then the real sprout breaks out through the soil mound and hands off to the footage. The underground shoot is rendered as a lit tube in `tools/bridge.py`; the one above the soil is the real footage.
- Sunflower pause: very subtle sway of flower, petals and leaves. Grass and trees move in a breeze. Sparse pollen, slow drift only.
- Sunflower centre is brown. She tried a different flower image, then asked to undo it.
- End of the story: no rain of seeds. The scene darkens and a single seed falls.

## Still to do
- Her real content: about text, projects, skills, email and links. Currently `[placeholders]`.
- Re-check the phone layout after any change.
