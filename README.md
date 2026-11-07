# Matcha Chiffon Cake

A single static recipe page: plain HTML and CSS, no build step, no dependencies, and no third-party requests at runtime.

## Preview

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. All asset paths are relative, so the page also works when served under `/baking/`.

## Test

```sh
python3 tests/static.py
```

Checks the exact recipe text, the asset references and the image dimensions, using only the Python standard library.

## Source faithfulness

The ingredients, quantities, sequence and portion counts come from the recipe's author and must not be changed or added to. Only typography (°F, ½, ¾) and light readability wording differ from the original. The page deliberately gives no prep time, yield, pan size, oil type, nutrition, doneness test, pan preparation or storage advice, because the recipe gives none.

## Credits

- `assets/cake.webp` is the author's own photograph of the finished cake, supplied for this page.
- [Newsreader](assets/fonts/Newsreader-OFL.txt) and [JetBrains Mono](assets/fonts/JetBrainsMono-OFL.txt) are used under the SIL Open Font License 1.1 and served from this repository.
