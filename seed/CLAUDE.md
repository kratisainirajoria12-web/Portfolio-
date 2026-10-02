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
| `hold/` | Her reference clip for the sunflower pause (camera eases back, flower sways, butterflies). Sheets of 4, 120 frames (24 fps clip, every 2nd frame), played at 12 fps forward and back; it starts on the last bloom frame and rewinds to it as the reader scrolls in or out (`holdT` in main.js) |
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
- Sprout (Day ~19–28): a sprout with a closed pointed bud pushes out of the cracked seed (her reference image). She asked twice for it thicker and for the soil to be closer to the seed: the soil now sits just above the seed and the camera tilts up a short way, then the real sprout breaks out through the soil mound and hands off to the footage. The underground shoot is rendered as a lit tube in `tools/bridge.py`; the one above the soil is the real footage.
- Sunflower pause: plays her reference video's motion (camera eases back, the flower sways, butterflies cross, grass moves). Sparse pollen, slow drift only.
- From the time the flower opens (bloom 248 on) and through the zoom-in, the flower is her reference flower (first frame of her clip, `tools/ref_v001.png`): `tools/head.py` puts it on each late bloom frame at that frame's flower size, and the zoom is a camera push into that frame. Her clip read frames from `reff/`; point `head.py` at `ref_v001.png` to rerun.
- Sunflower centre is dark brown like a real sunflower, matched to her reference video (`tools/recolor.py`, `tools/apply_disc.py`: bloom 240–279 and zoom/). No brown band on the petals: their bases reach the florets in yellow, as in the reference (`petal_fix`; the close-up zoom frames keep their own petal bases). She tried a different flower image, then asked to undo it.
- Ending: the zoom goes into the seeds at the heart of the flower, then dark brown closes in slowly from the edges (`#dip`, u 1520–1700 in main.js) until the screen is dark brown; the falling seed stays hidden in it, and the dark lifts only for Krati's meadow at the loop (1730–1795). She did not like a dark dip between the zoom and the seed head.
- End of the story: no rain of seeds. The scene darkens and a single seed falls.

## Still to do
- Her real content: about text, projects, skills, email and links. Currently `[placeholders]`.
- Re-check the phone layout after any change.
