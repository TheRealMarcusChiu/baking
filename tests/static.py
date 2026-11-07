#!/usr/bin/env python3
"""Dependency-free checks: exact recipe text, asset references, no runtime third parties."""
import re
import struct
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

INGREDIENTS = [
    "10 egg yolks",
    "½ cup of organic sugar",
    "¾ cup of oil",
    "1 cup of organic cake flour",
    "15–20 grams of matcha powder For each gram of matcha powder used, remove the same amount of cake flour.",
    "10 egg whites",
    "½ cup of organic sugar",
    "½ tsp cream of tartar",
]
METHOD = [
    "Break egg yolks.",
    "In 3 equal portions, whip in sugar until dissolved (batter should be yellowish-white).",
    "Add oil, flour, and matcha powder (sift the flour and matcha powder):",
    "Divide flour and matcha powder in 4 equal portions, oil in 3 equal portions.",
    "Add flour matcha portion, mix well.",
    "Add oil, mix well.",
    "Repeat until all portions mixed.",
    "Preheat oven at 275°F, so by the time we finish mixing bowl 1 & 2 we could immediately place it into oven.",
    "In clean bowl, beat egg whites and sugar until dissolved.",
    "Add cream of tartar. Whip until stiff peaks.",
    "Fold bowl 2 into bowl 1, until just mixed.",
    "Pour into tube-pan.",
    "Preheat oven at 275°F, then bake for 40 minutes.",
    "After 40 minutes, raise temp to 300°F and continue for another 20 minutes.",
    "Invert to cool.",
    "Remove from tube-pan when cool to touch (~2 hours).",
]
# (index into METHOD, <li> count when the figure opens, src, caption, alt)
PROCESS = [
    (1, 2, "assets/egg-yolk-mixture.webp", "Egg yolk mixture",
     "Yellow egg yolk mixture in the bottom of a stainless steel mixer bowl, with a wire whisk attachment raised above it."),
    (2, 7, "assets/matcha-batter.webp", "Matcha batter",
     "Glossy green matcha batter in the bottom of a metal bowl, seen from above."),
    (9, 10, "assets/whipped-egg-whites.webp", "Whipped egg whites",
     "White, glossy whipped egg white foam in swirled folds, filling a bowl."),
    (14, 15, "assets/cooling-cake.webp", "Cooling the cake upside down",
     "A baked cake still in its metal tube pan, turned upside down with the pan's center tube resting on the neck of a green glass bottle."),
    (15, 16, "assets/finished-cake.webp", "Finished matcha chiffon cake",
     "Finished green matcha chiffon ring cake on a white carrier base, with a blue-handled knife beside it."),
]
NOT_IN_SOURCE = ["toothpick", "skewer", "grease", "serves", "servings", "yield", "prep time",
                 "calorie", "nutrition", "refrigerat", "storage", "vegetable oil", "large egg", "tested"]


class Page(HTMLParser):
    """Collects each <li> in document order, per section id, with nested lists flattened.
    Figures inside an <li> are kept apart in self.figures, so captions never count as recipe text."""
    def __init__(self):
        super().__init__()
        self.tags = []
        self.items = {}
        self.ids = set()
        self.section = None
        self.open = []
        self.figures = []
        self.figure = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        self.ids.add(attrs.get("id"))
        if tag == "section":
            self.section = attrs.get("id")
        if tag == "li":
            self.open.append(len(self.items.setdefault(self.section, [])))
            self.items[self.section].append("")
        if tag == "figure" and self.open:
            self.figure = {"section": self.section, "depth": len(self.open), "count": len(self.items[self.section]),
                           "text": self.items[self.section][self.open[-1]], "caption": ""}
        if tag == "img" and self.figure:
            self.figure["img"] = attrs

    def handle_endtag(self, tag):
        if tag == "li":
            self.open.pop()
        if tag == "figure" and self.figure:
            self.figures.append(self.figure)
            self.figure = None

    def handle_data(self, data):
        if self.figure:
            self.figure["caption"] += data
        elif self.open:
            self.items[self.section][self.open[-1]] += data


def webp_size(path):
    data = path.read_bytes()[:40]
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", "cake.webp is not a WebP file"
    if data[12:16] == b"VP8X":
        return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
    if data[12:16] == b"VP8L":
        bits = struct.unpack("<I", data[21:25])[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    w, h = struct.unpack("<HH", data[26:30])
    return w & 0x3FFF, h & 0x3FFF


page = Page()
page.feed(HTML)
clean = lambda items: [" ".join(i.split()) for i in items]

assert clean(page.items["ingredients"]) == INGREDIENTS, clean(page.items["ingredients"])
assert clean(page.items["method"]) == METHOD, clean(page.items["method"])
assert [a.get("start") for t, a in page.tags if t == "ol"] == [None, "4", "7", "9"]

text = re.sub(r"<[^>]+>", " ", HTML).lower()
for word in NOT_IN_SOURCE:
    assert word not in text, f"not in the source recipe: {word}"
for fact in ["tube pan", "275°f for 40 minutes", "300°f for 20 minutes", "about 2 hours"]:
    assert fact in text, f"summary is missing: {fact}"

img = next(a for t, a in page.tags if t == "img")
assert img["src"] == "assets/cake.webp" and img["alt"]
assert (img["width"], img["height"]) == ("1440", "1920")
assert img["fetchpriority"] == "high" and img["loading"] == "eager"
assert webp_size(ROOT / img["src"]) == (1440, 1920)

assert [a.get("class") for t, a in page.tags if t == "figure"] == ["hero"] + ["process"] * len(PROCESS)
assert sum(t == "figcaption" for t, a in page.tags) == len(PROCESS) + 1
assert re.search(r'<figure class="hero"[^>]*>\s*<img [^>]*src="assets/cake\.webp"[^>]*>\s*'
                 r"<figcaption>yeaaa i know - looks like a stone wheel</figcaption>\s*</figure>", HTML)
assert [a["src"] for t, a in page.tags if t == "img"] == ["assets/cake.webp"] + [p[2] for p in PROCESS]
assert len(page.figures) == len(PROCESS)
for fig, (step, count, src, caption, alt) in zip(page.figures, PROCESS):
    # Exact step text before the figure plus the exact <li> check above means nothing follows it.
    assert (fig["section"], fig["depth"], fig["count"]) == ("method", 1, count), (src, fig)
    assert " ".join(fig["text"].split()) == METHOD[step], (src, fig["text"])
    assert " ".join(fig["caption"].split()) == caption, (src, fig["caption"])
    a = fig["img"]
    assert (a["src"], a["alt"]) == (src, alt), a
    assert (a["width"], a["height"], a["loading"], a["decoding"]) == ("960", "1280", "lazy", "async"), a
    assert webp_size(ROOT / src) == (960, 1280), src
assert ".process { margin: 16px 0 28px; width: 280px; max-width: 100%; }" in CSS
assert ".process img { display: block; width: 100%; height: auto; }" in CSS
assert "nav, .hero, .intro, .process, footer { display: none; }" in CSS
assert "Photos: the finished cake and recipe process." in HTML

assert "recipe" in page.ids and any(a.get("href") == "#recipe" for t, a in page.tags if t == "a")
assert 'onclick="window.print()"' in HTML
# Showcase: title and photo first, then one closed native disclosure holding everything else.
order = [HTML.index(s) for s in ("<h1>", 'class="hero"', '<details class="recipe-toggle">', "<summary>View recipe</summary>",
                                  'href="#recipe"', "window.print()", 'class="intro"', 'id="recipe"', 'id="notes"',
                                  "<footer>", "</details>")]
assert order == sorted(order), order
assert HTML.count("<details") == 1 and "<details open" not in HTML and HTML.count("<summary") == 1
assert HTML.count("<button") == 1 and HTML.count("<nav") == 1
assert '<script src="showcase.js" defer></script>' in HTML and (ROOT / "showcase.js").is_file()
JS = (ROOT / "showcase.js").read_text(encoding="utf-8")
for needle in ('"#recipe"', "hashchange", "beforeprint", "afterprint", "prefers-reduced-motion: reduce",
               "pointer: fine", '"touch"', "IntersectionObserver", "visibilitychange", "cancelAnimationFrame"):
    assert needle in JS, needle
assert not re.search(r"localStorage|sessionStorage|will-change|WebGL|import ", JS + CSS)
assert '<link rel="icon" href="favicon.svg" type="image/svg+xml">' in HTML
assert "#b7c785" in (ROOT / "favicon.svg").read_text(encoding="utf-8")
assert 'rel="canonical" href="https://git.marcuschiu.com/baking/"' in HTML
assert 'content="https://git.marcuschiu.com/baking/assets/cake.webp"' in HTML

local = [a[k] for t, a in page.tags for k in ("src", "href") if k in a and t != "meta"]
local += re.findall(r'url\("([^"]+)"\)', CSS)
for ref in local:
    if ref.startswith(("#", "data:")) or ref == "https://git.marcuschiu.com/baking/":
        continue
    assert not re.match(r"[a-z]+:|/", ref), f"not a relative reference: {ref}"
    assert (ROOT / ref).is_file(), f"missing asset: {ref}"

for font in ["Newsreader.ttf", "Newsreader-Italic.ttf", "JetBrainsMono.ttf", "Newsreader-OFL.txt", "JetBrainsMono-OFL.txt"]:
    assert (ROOT / "assets/fonts" / font).is_file(), font
assert (ROOT / ".nojekyll").is_file()
assert "gradient" not in CSS and "@import" not in CSS
assert "@media print" in CSS and "prefers-reduced-motion" in CSS
assert '<meta name="theme-color" content="#0f0c09">' in HTML
for token in ["--background: #0f0c09", "--primary: #ece1cf", "--body: #cdc1ab", "--muted: #a99e88",
              "--border: #2a2218", "--panel: #14110b", "--matcha: #b7c785"]:
    assert token in CSS, token
assert not re.search(r"--(ivory|forest|sage)\b", CSS)

print("ok")
