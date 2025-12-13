#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


SPAN_RE = re.compile(r'<span><i class="fa-solid fa-tags"></i>\s*(.*?)</span>', re.DOTALL)
LINK_RE = re.compile(r'<a href="/tags/([^/]+)/">([^<]+)</a>')

_CENTURY_RE = re.compile(r"^(\d+)(st|nd|rd|th)-century$")


def desired_label(slug: str) -> str:
    overrides: dict[str, str] = {
        "ai": "AI",
        "llm": "LLM",
        "dna": "DNA",
        "williams": "Williams",
        "bernard-williams": "Bernard Williams",
        "wittgenstein": "Wittgenstein",
        "nietzsche": "Nietzsche",
        "hume": "Hume",
        "foucault": "Foucault",
        "engel": "Engel",
        "rickert": "Rickert",
        "windelband": "Windelband",
        "wolf": "Wolf",
        "krishnan": "Krishnan",
        "fricker": "Fricker",
        "craig": "Craig",
        "meta-philosophy": "metaphilosophy",
        "non-domination": "non-domination",
        "reasons-vs-causes": "reasons vs. causes",
    }
    if slug in overrides:
        return overrides[slug]

    m = _CENTURY_RE.match(slug)
    if m:
        return f"{m.group(1)}{m.group(2)} century"

    label = slug.replace("-", " ")

    # Hyphenated compounds that read better with hyphens.
    label = label.replace("knowledge first", "knowledge-first")
    label = label.replace("non ideal", "non-ideal")
    label = label.replace("non domination", "non-domination")

    # Common abbreviations / proper nouns.
    label = re.sub(r"\bai\b", "AI", label)
    label = re.sub(r"\bllm\b", "LLM", label)
    label = re.sub(r"\bdna\b", "DNA", label)

    label = label.replace("bernard williams", "Bernard Williams")
    label = re.sub(r"\bwilliams\b", "Williams", label)

    # Punctuation tweaks.
    label = label.replace(" vs ", " vs. ")
    return label


def rewrite_span(span_html: str) -> str:
    slugs = [m.group(1) for m in LINK_RE.finditer(span_html)]
    if not slugs:
        return span_html
    links = [f'<a href="/tags/{slug}/">{desired_label(slug)}</a>' for slug in slugs]
    return f'<span><i class="fa-solid fa-tags"></i> {", ".join(links)}</span>'


def process_file(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    m = SPAN_RE.search(text)
    if not m:
        return False

    old_span = m.group(0)
    new_span = rewrite_span(old_span)
    if new_span == old_span:
        return False

    new_text = text[: m.start()] + new_span + text[m.end() :]
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize the displayed labels of the 6-tag span in EN entries.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes.")
    parser.add_argument("--entries", default="content/entries", help="Entries directory (default: content/entries).")
    args = parser.parse_args()

    entries_dir = Path(args.entries)
    changed: list[Path] = []
    for path in sorted(entries_dir.glob("*.md")):
        if path.name.endswith(".fr.md") or path.name.endswith(".de.md"):
            continue
        if process_file(path, dry_run=args.dry_run):
            changed.append(path)

    for p in changed:
        print(p)
    print(f"CHANGED_FILES {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
