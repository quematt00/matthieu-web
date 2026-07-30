#!/usr/bin/env python3
"""Build the site's Font Awesome WOFF2 subsets from the upstream TTF files.

The Font Awesome CSS and class names remain unchanged. This script scans the
site and theme sources, resolves every referenced icon class through the
vendored Font Awesome CSS, and writes reduced WOFF2 files at the existing URLs.
Run it from any directory after installing requirements-fontawesome.txt.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "themes" / "FixIt"
CSS = THEME / "assets" / "lib" / "fontawesome-free" / "all.min.css"
WEBFONTS = THEME / "static" / "lib" / "webfonts"

FONT_FILES = (
    ("fa-solid-900.ttf", "fa-solid-900.woff2"),
    ("fa-regular-400.ttf", "fa-regular-400.woff2"),
    ("fa-brands-400.ttf", "fa-brands-400.woff2"),
)

SOURCE_SUFFIXES = {
    ".html",
    ".js",
    ".json",
    ".md",
    ".scss",
    ".toml",
    ".yaml",
    ".yml",
}
SKIP_PARTS = {".git", "node_modules", "public", "resources"}
ICON_TOKEN = re.compile(r"\bfa-[a-z0-9][a-z0-9-]*\b")
ICON_RULE = re.compile(r"([^{}]+)\{--fa:\"\\([0-9a-fA-F]+)\"")


def source_files() -> list[Path]:
    files: list[Path] = []
    for base in (ROOT, THEME):
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            relative = path.relative_to(base)
            if any(part in SKIP_PARTS for part in relative.parts):
                continue
            if base == THEME and relative.parts[:2] == ("assets", "lib"):
                continue
            files.append(path)
    return sorted(set(files))


def referenced_tokens() -> set[str]:
    tokens: set[str] = set()
    for path in source_files():
        tokens.update(ICON_TOKEN.findall(path.read_text(encoding="utf-8")))
    return tokens


def icon_map() -> dict[str, int]:
    css = CSS.read_text(encoding="utf-8")
    mapping: dict[str, int] = {}
    for selectors, hexadecimal in ICON_RULE.findall(css):
        codepoint = int(hexadecimal, 16)
        for token in ICON_TOKEN.findall(selectors):
            mapping[token] = codepoint
    return mapping


def required_codepoints() -> tuple[set[int], set[str], set[str]]:
    tokens = referenced_tokens()
    mapping = icon_map()
    icons = tokens & mapping.keys()
    utilities = tokens - mapping.keys()
    return {mapping[token] for token in icons}, icons, utilities


def font_codepoints(path: Path) -> set[int]:
    with TTFont(path, lazy=True) as font:
        return set((font.getBestCmap() or {}).keys())


def build_subset(source: Path, destination: Path, codepoints: set[int]) -> None:
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6]
    options.name_legacy = True
    options.name_languages = [0x0409]
    options.recalc_timestamp = False

    font = subset.load_font(str(source), options, lazy=False)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)
    subset.save_font(font, str(destination), options)


def verify(codepoints: set[int]) -> None:
    for input_name, output_name in FONT_FILES:
        source = WEBFONTS / input_name
        output = WEBFONTS / output_name
        if not output.exists():
            raise SystemExit(f"Missing generated font: {output}")
        expected = codepoints & font_codepoints(source)
        missing = expected - font_codepoints(output)
        if missing:
            rendered = ", ".join(f"U+{codepoint:04X}" for codepoint in sorted(missing))
            raise SystemExit(f"{output_name} is missing required glyphs: {rendered}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed WOFF2 subsets without rewriting them",
    )
    args = parser.parse_args()

    codepoints, icons, utilities = required_codepoints()
    if not codepoints:
        raise SystemExit("No Font Awesome icon references were found")

    if not args.check:
        for input_name, output_name in FONT_FILES:
            build_subset(WEBFONTS / input_name, WEBFONTS / output_name, codepoints)

    verify(codepoints)

    print(f"Font Awesome: {len(icons)} icon classes, {len(codepoints)} codepoints")
    print(f"Ignored {len(utilities)} Font Awesome utility/style classes")
    for _, output_name in FONT_FILES:
        output = WEBFONTS / output_name
        print(f"{output_name}: {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
