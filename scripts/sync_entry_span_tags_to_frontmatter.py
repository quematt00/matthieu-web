#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import i18n_tags
import normalize_fr_tags


SPAN_BLOCK_RE = re.compile(r'<span><i class="fa-solid fa-tags"></i>.*?</span>', re.DOTALL)


@dataclass(frozen=True)
class EntryLang:
    lang: str  # "en" | "fr" | "de"
    href_prefix: str


def entry_lang_for_path(path: Path) -> EntryLang | None:
    name = path.name
    if name.endswith(".fr.md"):
        return EntryLang("fr", "/fr/tags/")
    if name.endswith(".de.md"):
        return EntryLang("de", "/de/tags/")
    if name.endswith(".md"):
        return EntryLang("en", "/tags/")
    return None


def split_frontmatter(text: str) -> tuple[list[str], list[str], list[str]] | None:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return (lines[:1], lines[1:i], lines[i:])
    return None


def parse_inline_array(array_text: str) -> list[str]:
    items: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in array_text:
        if quote is not None:
            if ch == quote:
                quote = None
            else:
                buf.append(ch)
            continue
        if ch in ("'", '"'):
            quote = ch
            continue
        if ch == ",":
            item = "".join(buf).strip()
            if item:
                items.append(item)
            buf = []
            continue
        buf.append(ch)
    last = "".join(buf).strip()
    if last:
        items.append(last)
    return items


def format_inline_array(items: list[str]) -> str:
    return "[" + ", ".join([f"\"{i}\"" for i in items]) + "]"


def parse_frontmatter_tags(fm_lines: list[str]) -> tuple[list[str], str, int | None]:
    """
    Returns: (tags, style, tags_line_index)
      style in {"inline", "block", "missing"}
    """
    for i, line in enumerate(fm_lines):
        m_inline = re.match(r"^tags:\s*(\[.*\])\s*$", line.strip())
        if m_inline:
            array = m_inline.group(1).strip()
            inner = array[1:-1].strip()
            tags = parse_inline_array(inner) if inner else []
            return tags, "inline", i
        if line.strip() == "tags:":
            tags: list[str] = []
            j = i + 1
            while j < len(fm_lines):
                l2 = fm_lines[j]
                if re.match(r"^\w", l2):
                    break
                m_item = re.match(r"^\s*-\s*(.*?)\s*$", l2.strip())
                if m_item:
                    raw = m_item.group(1).strip()
                    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                        raw = raw[1:-1]
                    tags.append(raw)
                j += 1
            return tags, "block", i
    return [], "missing", None


def replace_frontmatter_tags(
    fm_lines: list[str], new_tags: list[str], style: str, tags_line_index: int | None
) -> list[str]:
    if style == "inline" and tags_line_index is not None:
        out = list(fm_lines)
        out[tags_line_index] = f"tags: {format_inline_array(new_tags)}\n"
        return out

    if style == "block" and tags_line_index is not None:
        out: list[str] = []
        i = 0
        while i < len(fm_lines):
            line = fm_lines[i]
            if i == tags_line_index and line.strip() == "tags:":
                out.append(line)
                i += 1
                while i < len(fm_lines):
                    l2 = fm_lines[i]
                    if re.match(r"^\w", l2):
                        break
                    i += 1
                for t in new_tags:
                    out.append(f"  - \"{t}\"\n")
                continue
            out.append(line)
            i += 1
        return out

    insertion_index = 0
    for i, line in enumerate(fm_lines):
        if line.strip().startswith(("title:", "year:", "date:", "draft:", "categories:", "summary:", "description:")):
            insertion_index = i + 1
    tags_block = ["tags:\n"] + [f"  - \"{t}\"\n" for t in new_tags]
    return fm_lines[:insertion_index] + tags_block + fm_lines[insertion_index:]


def extract_span_slugs(text: str, href_prefix: str) -> list[str]:
    m = SPAN_BLOCK_RE.search(text)
    if not m:
        return []
    span_html = m.group(0)
    return re.findall(r'href="' + re.escape(href_prefix) + r'([^/]+)/"', span_html)


def build_slug_to_term(entries_dir: Path, lang: str) -> dict[str, str]:
    pattern = "*.md" if lang == "en" else f"*.{lang}.md"
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for path in entries_dir.glob(pattern):
        if lang == "en" and (path.name.endswith(".fr.md") or path.name.endswith(".de.md")):
            continue
        text = path.read_text(encoding="utf-8")
        parts = split_frontmatter(text)
        if parts is None:
            continue
        _, fm_lines, _ = parts
        tags, _, _ = parse_frontmatter_tags(fm_lines)
        for t in tags:
            slug = i18n_tags.taxonomy_slug(t)
            counts[slug][t] += 1
    slug_to_term: dict[str, str] = {}
    for slug, counter in counts.items():
        slug_to_term[slug] = counter.most_common(1)[0][0]
    return slug_to_term


def normalize_term(term: str, lang: str) -> str:
    if lang == "fr":
        return normalize_fr_tags.normalize_tag(term)
    return term


def canonical_term_for_slug(slug: str, lang: str, slug_to_term: dict[str, str]) -> str:
    if lang == "en":
        return slug

    if lang == "fr":
        fr_overrides = {
            "blame": "blâme",
        }
        if slug in fr_overrides:
            return normalize_term(fr_overrides[slug], lang)

    if slug in slug_to_term:
        return normalize_term(slug_to_term[slug], lang)
    return normalize_term(slug, lang)


def sync_file(path: Path, slug_to_term: dict[str, str], dry_run: bool) -> bool:
    lang_info = entry_lang_for_path(path)
    if lang_info is None:
        return False

    text = path.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if parts is None:
        return False
    head, fm_lines, tail = parts

    span_slugs = extract_span_slugs(text, lang_info.href_prefix)
    if not span_slugs:
        return False

    tags, style, tags_line_index = parse_frontmatter_tags(fm_lines)
    have_slugs = {i18n_tags.taxonomy_slug(t) for t in tags}

    new_tags = list(tags)
    changed = False
    for slug in span_slugs:
        if slug in have_slugs:
            continue
        term = canonical_term_for_slug(slug, lang_info.lang, slug_to_term)
        if not term:
            continue
        new_tags.append(term)
        have_slugs.add(i18n_tags.taxonomy_slug(term))
        changed = True

    if not changed:
        return False

    new_fm_lines = replace_frontmatter_tags(fm_lines, new_tags, style, tags_line_index)
    new_text = "".join(head + new_fm_lines + tail)
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensure the in-body 6-tag span tags are present in the entry frontmatter tags."
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes.")
    parser.add_argument("--entries", default="content/entries", help="Entries directory (default: content/entries).")
    args = parser.parse_args()

    entries_dir = Path(args.entries)

    slug_to_term_fr = build_slug_to_term(entries_dir, "fr")
    slug_to_term_de = build_slug_to_term(entries_dir, "de")

    changed: list[Path] = []
    for path in sorted(entries_dir.glob("*.md")):
        if sync_file(path, {}, dry_run=args.dry_run):
            changed.append(path)
    for path in sorted(entries_dir.glob("*.fr.md")):
        if sync_file(path, slug_to_term_fr, dry_run=args.dry_run):
            changed.append(path)
    for path in sorted(entries_dir.glob("*.de.md")):
        if sync_file(path, slug_to_term_de, dry_run=args.dry_run):
            changed.append(path)

    for p in changed:
        print(p)
    print(f"CHANGED_FILES {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
