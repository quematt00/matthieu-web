from __future__ import annotations

import argparse
import re
from typing import Any

from i18n_tags import translate_tag


def parse_frontmatter(text: str) -> dict[str, Any]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError("Missing frontmatter")
    fm = m.group(1)
    title = None
    year = None
    tags: list[str] = []
    categories: list[str] = []

    mode: str | None = None
    for raw_line in fm.splitlines():
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue
        if re.match(r"^[a-zA-Z0-9_-]+:", line):
            key, rest = line.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            mode = key if rest == "" else None
            if key == "title":
                title = rest.strip().strip('"').strip("'")
            elif key == "year":
                year = rest.strip().strip('"').strip("'")
            continue
        if mode == "tags":
            m_item = re.match(r'^\s*-\s*("?)(.*?)\1\s*$', line)
            if m_item:
                tags.append(m_item.group(2))
            continue
        if mode == "categories":
            m_item = re.match(r'^\s*-\s*("?)(.*?)\1\s*$', line)
            if m_item:
                categories.append(m_item.group(2))
            continue

    if title is None or year is None:
        raise ValueError("Frontmatter missing title/year")
    return {"title": title, "year": year, "tags": tags, "categories": categories}


_CATEGORY_TRANSLATIONS: dict[str, dict[str, str]] = {
    "history of philosophy": {"fr": "histoire de la philosophie", "de": "Geschichte der Philosophie"},
    "practical philosophy": {"fr": "philosophie pratique", "de": "Praktische Philosophie"},
    "theoretical philosophy": {"fr": "philosophie théorique", "de": "Theoretische Philosophie"},
}

_YEAR_TRANSLATIONS: dict[str, dict[str, str]] = {
    "forthcoming": {"fr": "à paraître", "de": "im Erscheinen"},
}


def translate_entry_frontmatter(frontmatter: dict[str, Any], lang: str) -> str:
    year = frontmatter["year"]
    year = _YEAR_TRANSLATIONS.get(year, {}).get(lang, year)

    tags = [translate_tag(t, lang).term for t in (frontmatter.get("tags") or [])]

    categories = []
    for c in frontmatter.get("categories") or []:
        categories.append(_CATEGORY_TRANSLATIONS.get(c, {}).get(lang, c))

    lines: list[str] = ["---"]
    lines.append(f'title: "{frontmatter["title"]}"')
    lines.append(f'year: "{year}"')
    lines.append("tags:")
    for t in tags:
        lines.append(f'  - "{t}"')
    lines.append("categories:")
    for c in categories:
        lines.append(f'  - "{c}"')
    lines.append("---")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--lang", choices=["fr", "de"], required=True)
    args = ap.parse_args()

    text = open(args.path, "r", encoding="utf-8").read()
    fm = parse_frontmatter(text)
    print(translate_entry_frontmatter(fm, args.lang))


if __name__ == "__main__":
    main()

