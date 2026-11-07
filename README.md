# Matcha Chiffon Cake

A single static recipe page: plain HTML and CSS plus one small script, no build step, no dependencies, and no third-party requests at runtime.

## Showcase

The first screen is the title, the whole original cake photograph and one **View recipe** control. The recipe sits in a native `<details>` element, so it opens with a click or the keyboard even without JavaScript. Links to `#recipe` open it, and printing always includes the full recipe on one page, whether it is open or closed.

`showcase.js` tilts the photograph by at most 6° on each axis (plus up to 12 pixels of shift, in 1000px perspective) as a mouse moves across the window, easing back to rest at the center, when the pointer leaves the window, or when the window loses focus. It is a flat photograph turning slightly in CSS perspective, not a 3D model of the cake: no depth map, WebGL, cropping or recoloring. The photo is loaded and shown first; the motion starts only afterwards. It stays still for touch, coarse pointers and reduced-motion settings, and animation frames run only while the photo is settling after pointer movement, never while idle, hidden or scrolled out of view.

Limitations: process photographs inside the closed recipe are lazy-loaded only when JavaScript is on. Browsers turn native lazy loading off when scripting is disabled, so without JavaScript all of them download up front. The motion was checked in Chromium and WebKit test engines, not on physical Safari or iOS devices.

Sources: web.dev, "How to create high-performance CSS animations"; MDN, "Animation performance and frame rate"; the HTML Standard's lazy-loading rules.

## Preview

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. All asset paths are relative, so the page also works when served under `/baking/`.

## Test

```sh
python3 tests/static.py
```

Checks the exact recipe text, the asset references, the image dimensions and the showcase structure (one closed disclosure, recipe, print and link inside it), using only the Python standard library.

## Source faithfulness

The ingredients, quantities, sequence and portion counts come from the recipe's author and must not be changed or added to. Only typography (°F, ½, ¾) and light readability wording differ from the original. The page deliberately gives no prep time, yield, pan size, oil type, nutrition, doneness test, pan preparation or storage advice, because the recipe gives none.

## Credits

- `assets/cake.webp` is the author's own photograph of the finished cake, supplied for this page.
- `assets/egg-yolk-mixture.webp`, `assets/matcha-batter.webp`, `assets/whipped-egg-whites.webp` and `assets/cooling-cake.webp` are photographs of the recipe process, supplied for this page.
- [Newsreader](assets/fonts/Newsreader-OFL.txt) and [JetBrains Mono](assets/fonts/JetBrainsMono-OFL.txt) are used under the SIL Open Font License 1.1 and served from this repository.
