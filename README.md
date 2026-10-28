# Lyanna Nguyen — Portfolio

A cozy pixel-farm portfolio for Lyanna Nguyen, Product Designer & UX Researcher.
Plain HTML, CSS and JavaScript — no build step, no dependencies.

## Pages

| File | Page |
| --- | --- |
| `index.html` | Home — hero, knock-on-the-door greeting, selected work, contact footer |
| `about.html` | About — intro, photos, songs on repeat |
| `garden.html` | Design Garden — filterable gallery of visual, illustration and photo work |
| `triceratops.html` | Case study: Triceratops Website |
| `linguistics-club.html` | Case study: Linguistics Club Website |
| `prototypes/linguistics-club.html` | Interactive prototype embedded in the Linguistics Club case study |

## Structure

```
css/pixel-pals.css   design-system components (frames, buttons, stickers…)
css/site.css         design tokens, animations and page styles
css/case-study.css   extra rules for the case-study pages
css/board.css        town bulletin board on the home page
css/cs-components.css  hand-written case-study blocks (stat row, options, annotations, placeholders)
js/site.js           shared helpers: data-show toggles, data-action clicks, scroll reveals
js/home.js           opening animation, door knock + dialogue, fireflies
js/board.js          bulletin board: drag or arrow-key hobby notes to re-pin them
partials/board.html  bulletin board notes, inserted into index.html by the converter
js/about.js          song previews (Spotify embeds)
js/garden.js         gallery filter tabs
js/case-study.js     table-of-contents scroll spy, before/after switch, research toggle
assets/images/       images and pixel sprites
assets/fonts/        fonts used by the prototype
assets/files/        Lyanna_Nguyen_Resume.pdf
tools/convert_export.py  regenerates the pages from a single-file design export
tools/pixel/stickers.py  draws the bulletin board's pixel hobby stickers (assets/images/sticker-*.svg)
tools/pixel/backdrop.py  draws the home hero's 8-bit mountains, hills, trees and grass (assets/images/bg-*.svg)
```

`triceratops.html` is hand-built (it follows the 2026 case-study structure), so the converter
skips it. Media still to come are dashed `.ph` placeholders; search the page for `class="ph` to
find them, and see the comment in the hero for how to drop in the looping video.

Interactive bits use two attributes:

- `data-show="name"` — elements the scripts show/hide (`Site.show('name', true)`).
- `data-action="name"` — clickable elements handled by `Site.on('name', fn)`.

## Run locally

Any static server works:

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy

The site is fully static, so it can go on GitHub Pages (Settings → Pages → deploy from the
`main` branch, root folder), Netlify, Vercel or Cloudflare Pages as-is. `.nojekyll` is
included so GitHub Pages serves every file untouched.
