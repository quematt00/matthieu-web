#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SPAN_RE = re.compile(r'<span><i class="fa-solid fa-tags"></i>\s*(.*?)</span>', re.DOTALL)
LINK_RE = re.compile(r'<a href="/tags/([^/]+)/">([^<]+)</a>')


BLACKLIST = {
    "en": {"conceptual-history", "practical-reason", "reasons"},
    "fr": {"histoire-conceptuelle", "raison-pratique", "raisons"},
    "de": {"begriffsgeschichte", "praktische-gruende", "gruende"},
}


SPAN_REPLACEMENTS: dict[str, list[str]] = {
    "conceptual-engineering.md": [
        "analytic-philosophy",
        "conceptual-engineering",
        "conceptual-change",
        "analysis",
        "handbuch",
        "conceptual-adaptation",
    ],
    "foucault-et-engel-sur-la-normativit-des-normes-du-savoir.md": [
        "normativity",
        "truth",
        "conceptual-change",
        "systematicity",
        "foucault",
        "engel",
    ],
    "genealogy-evaluation-and-engineering.md": [
        "conceptual-engineering",
        "legitimacy",
        "genealogy",
        "genealogical-method",
        "ideology-critique",
        "conceptual-ethics",
    ],
    "needs-of-the-mind-how-the-aptic-normativity-of-needs-can-guide-conceptual-adaptation.md": [
        "conceptual-adaptation",
        "needs",
        "aptic-normativity",
        "privacy",
        "technology",
        "power",
    ],
    "on-the-normativity-of-explications.md": [
        "normativity",
        "explication",
        "rickert",
        "windelband",
        "conceptual-change",
        "theoretical-philosophy",
    ],
    "reasons-of-love-and-conceptual-good-for-nothings.md": [
        "concepts",
        "conceptual-ethics",
        "conceptual-engineering",
        "motivation",
        "reasons-of-love",
        "normativity",
    ],
    "the-authority-and-politics-of-epiphanic-experience.md": [
        "authority",
        "politics",
        "epiphanies",
        "experience",
        "conceptual-change",
        "practical-philosophy",
    ],
    "the-romantic-roots-of-internalism.md": [
        "internalism",
        "internal-reasons",
        "romanticism",
        "conceptual-change",
        "history-of-philosophy",
        "krishnan",
    ],
    "whence-the-demand-for-ethical-theory.md": [
        "public-reason",
        "ethical-theory",
        "genealogy",
        "metaethics",
        "legitimacy",
        "conceptual-change",
    ],
    "why-we-care-about-understanding-competence-through-predictive-compression.md": [
        "epistemology",
        "social-epistemology",
        "understanding",
        "conceptual-change",
        "compression",
        "competence",
    ],
}


@dataclass(frozen=True)
class Frontmatter:
    head: list[str]
    body: list[str]
    tail: list[str]


def split_frontmatter(text: str) -> Frontmatter | None:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return Frontmatter(lines[:1], lines[1:i], lines[i:])
    return None


def _parse_inline_array(array_text: str) -> list[str]:
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


def _format_inline_array(items: list[str]) -> str:
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
            tags = _parse_inline_array(inner) if inner else []
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
        out[tags_line_index] = f"tags: {_format_inline_array(new_tags)}\n"
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

    # Insert block tags near other top-level keys.
    insertion_index = 0
    for i, line in enumerate(fm_lines):
        if line.strip().startswith(("title:", "year:", "date:", "draft:", "categories:", "summary:", "description:")):
            insertion_index = i + 1
    tags_block = ["tags:\n"] + [f"  - \"{t}\"\n" for t in new_tags]
    return fm_lines[:insertion_index] + tags_block + fm_lines[insertion_index:]


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

    label = slug.replace("-", " ")
    label = label.replace("knowledge first", "knowledge-first")
    label = label.replace("non ideal", "non-ideal")
    label = label.replace("non domination", "non-domination")
    label = re.sub(r"\bai\b", "AI", label)
    label = re.sub(r"\bllm\b", "LLM", label)
    label = re.sub(r"\bdna\b", "DNA", label)
    label = label.replace("bernard williams", "Bernard Williams")
    label = re.sub(r"\bwilliams\b", "Williams", label)
    label = label.replace(" vs ", " vs. ")
    return label


def build_span(slugs: list[str]) -> str:
    links = [f'<a href="/tags/{slug}/">{desired_label(slug)}</a>' for slug in slugs]
    return f'<span><i class="fa-solid fa-tags"></i> {", ".join(links)}</span>'


def remove_blacklisted_tags(tags: list[str], lang: str) -> list[str]:
    black = BLACKLIST[lang]
    return [t for t in tags if t not in black]


def process_file(path: Path, lang: str, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    fm = split_frontmatter(text)
    if fm is None:
        return False

    tags, style, tags_line_index = parse_frontmatter_tags(fm.body)
    new_tags = remove_blacklisted_tags(tags, lang)
    changed = new_tags != tags

    # EN: rewrite the 6-tag span if configured.
    new_text = text
    if lang == "en":
        replacement_slugs = SPAN_REPLACEMENTS.get(path.name)
        if replacement_slugs is not None:
            # Ensure span tags are present in frontmatter tags.
            for slug in replacement_slugs:
                if slug not in new_tags:
                    new_tags.append(slug)
                    changed = True

            span = build_span(replacement_slugs)
            m = SPAN_RE.search(new_text)
            if not m:
                raise ValueError(f"Missing tag span in {path}")
            old_span = m.group(0)
            if old_span != span:
                new_text = new_text[: m.start()] + span + new_text[m.end() :]
                changed = True
        else:
            m = SPAN_RE.search(new_text)
            if m:
                span_slugs = [m2.group(1) for m2 in LINK_RE.finditer(m.group(0))]
                remaining = sorted(set(span_slugs) & BLACKLIST["en"])
                if remaining:
                    raise ValueError(f"{path} still contains blacklisted span tags: {remaining}")

    if not changed:
        return False

    new_fm_body = replace_frontmatter_tags(fm.body, new_tags, style, tags_line_index)
    rebuilt = "".join(fm.head + new_fm_body + fm.tail)

    if lang == "en":
        # Keep any span changes already applied to new_text, but re-inject updated frontmatter.
        fm2 = split_frontmatter(new_text)
        if fm2 is None:
            raise ValueError(f"Missing frontmatter after edits in {path}")
        rebuilt = "".join(fm2.head + new_fm_body + fm2.tail)

    if not dry_run:
        path.write_text(rebuilt, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove gap-filler tags (conceptual history / practical reason / reasons and translations) "
        "from frontmatter across all languages, and replace them in EN 6-tag spans with more descriptive tags."
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes.")
    parser.add_argument("--entries", default="content/entries", help="Entries directory (default: content/entries).")
    args = parser.parse_args()

    entries_dir = Path(args.entries)
    changed: list[Path] = []

    for path in sorted(entries_dir.glob("*.md")):
        if path.name.endswith(".fr.md") or path.name.endswith(".de.md"):
            continue
        if process_file(path, "en", dry_run=args.dry_run):
            changed.append(path)

    for path in sorted(entries_dir.glob("*.fr.md")):
        if process_file(path, "fr", dry_run=args.dry_run):
            changed.append(path)

    for path in sorted(entries_dir.glob("*.de.md")):
        if process_file(path, "de", dry_run=args.dry_run):
            changed.append(path)

    for p in changed:
        print(p)
    print(f"CHANGED_FILES {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
