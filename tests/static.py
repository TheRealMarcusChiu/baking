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
NOT_IN_SOURCE = ["toothpick", "skewer", "grease", "serves", "servings", "yield", "prep time",
                 "calorie", "nutrition", "refrigerat", "storage", "vegetable oil", "large egg", "tested"]


class Page(HTMLParser):
    """Collects each <li> in document order, per section id, with nested lists flattened."""
    def __init__(self):
        super().__init__()
        self.tags = []
        self.items = {}
        self.ids = set()
        self.section = None
        self.open = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        self.ids.add(attrs.get("id"))
        if tag == "section":
            self.section = attrs.get("id")
        if tag == "li":
            self.open.append(len(self.items.setdefault(self.section, [])))
            self.items[self.section].append("")

    def handle_endtag(self, tag):
        if tag == "li":
            self.open.pop()

    def handle_data(self, data):
        if self.open:
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

assert "recipe" in page.ids and any(a.get("href") == "#recipe" for t, a in page.tags if t == "a")
assert 'onclick="window.print()"' in HTML
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

print("ok")
