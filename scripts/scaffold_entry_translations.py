from __future__ import annotations

import glob
import os
import re
from typing import Any

from i18n_tags import translate_tag


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("Missing frontmatter")
    fm_text, body = m.group(1), m.group(2)

    title = None
    year = None
    tags: list[str] = []
    categories: list[str] = []

    mode: str | None = None
    for raw_line in fm_text.splitlines():
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

    return {"title": title, "year": year, "tags": tags, "categories": categories}, body


_CATEGORY_TRANSLATIONS: dict[str, dict[str, str]] = {
    "history of philosophy": {"fr": "histoire de la philosophie", "de": "Geschichte der Philosophie"},
    "practical philosophy": {"fr": "philosophie pratique", "de": "Praktische Philosophie"},
    "theoretical philosophy": {"fr": "philosophie théorique", "de": "Theoretische Philosophie"},
}

_YEAR_TRANSLATIONS: dict[str, dict[str, str]] = {
    "forthcoming": {"fr": "à paraître", "de": "im Erscheinen"},
}


def render_frontmatter(fm: dict[str, Any], lang: str) -> str:
    year = _YEAR_TRANSLATIONS.get(fm["year"], {}).get(lang, fm["year"])
    tags = [translate_tag(t, lang).term for t in (fm.get("tags") or [])]
    categories = [
        _CATEGORY_TRANSLATIONS.get(c, {}).get(lang, c) for c in (fm.get("categories") or [])
    ]

    lines: list[str] = ["---"]
    lines.append(f'title: "{fm["title"]}"')
    lines.append(f'year: "{year}"')
    lines.append("tags:")
    for t in tags:
        lines.append(f'  - "{t}"')
    lines.append("categories:")
    for c in categories:
        lines.append(f'  - "{c}"')
    lines.append("---")
    return "\n".join(lines)


_TAGS_SPAN_RE = re.compile(r"^<span><i class=\"fa-solid fa-tags\"></i>.*</span>\s*$", re.M)


def rewrite_body(body: str, lang: str) -> str:
    # Replace the hardcoded tag list with a shortcode that uses frontmatter tags.
    body = _TAGS_SPAN_RE.sub("{{< entry-tags >}}", body)

    # Translate the download link label (keep the title inside aria-label).
    def repl_aria(m: re.Match[str]) -> str:
        title = m.group(1)
        if lang == "fr":
            return f'aria-label="Télécharger le PDF de {title}"'
        if lang == "de":
            return f'aria-label="PDF von {title} herunterladen"'
        return m.group(0)

    body = re.sub(r'aria-label="Download PDF of ([^"]+)"', repl_aria, body)

    if lang == "fr":
        body = body.replace("> Download PDF", "> Télécharger le PDF")
    elif lang == "de":
        body = body.replace("> Download PDF", "> PDF herunterladen")

    return body.strip() + "\n"


def scaffold_file(src_path: str, lang: str) -> str:
    text = open(src_path, "r", encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    out_fm = render_frontmatter(fm, lang)
    out_body = rewrite_body(body, lang)
    return out_fm + "\n\n" + out_body


def main() -> None:
    root = "content/entries"
    src_paths = sorted(glob.glob(os.path.join(root, "*.md")))
    src_paths = [p for p in src_paths if not re.search(r"\.(fr|de)\.md$", p)]

    for src in src_paths:
        base = src[:-3]
        for lang in ("fr", "de"):
            dest = f"{base}.{lang}.md"
            if os.path.exists(dest):
                continue
            out = scaffold_file(src, lang)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(out)


if __name__ == "__main__":
    main()
