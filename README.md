# Krati — Portfolio

A personal portfolio for a UI/UX & product designer, built around a handcrafted 3D clay caricature that guides visitors through the site.

Static HTML/CSS/JS — no framework, no build step. The clay props (desk, lamp, plant, service objects, process “lump”) are made in CSS, so the page stays light and fast; the caricature is the one image.

## Structure

```
index.html                 Home: hero · what I do · selected work · about · approach · contact
work/*.html                Case studies (generated — see below)
css/base.css               Design tokens, type, nav, buttons, the .clay material
css/home.css               Home page scenes and sections
css/case.css               Case study layout and before/after mock screens
js/main.js                 Scroll camera, parallax, reveals, process steps, closing scene
assets/krati.webp          Caricature (background removed)
tools/build_cases.py       Case study content + template
```

## Run locally

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

## Editing case studies

All case-study copy lives in `tools/build_cases.py`. Edit it, then regenerate:

```sh
python3 tools/build_cases.py
```

The cover art for each case study comes from the matching project stage in `index.html`, so the two always match.

## Before publishing

- Replace `hello@example.com` in `index.html` with your real address.
- Add your résumé PDF and LinkedIn/Behance/Dribbble links (the `href="#"` placeholders).
- Case-study copy is a structured first draft. Check every detail against what actually happened, and add your measured results in each **Outcomes** section.

## Accessibility & motion

- Semantic landmarks, skip link, visible focus states, and keyboard-reachable interactions.
- All decorative scenes are `aria-hidden`; the before/after screens have text alternatives.
- `prefers-reduced-motion` turns off the idle animation, parallax and scroll-driven scenes. The closing scene then shows as a still composition. It does the same on small screens.
