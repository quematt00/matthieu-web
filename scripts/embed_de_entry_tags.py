#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

import i18n_tags
import normalize_de_tags


ENTRY_TAGS_SHORTCODE = "{{< entry-tags >}}"

EN_SPAN_RE = re.compile(r'<span><i class="fa-solid fa-tags"></i>\s*(.*?)</span>', re.DOTALL)
EN_LINK_RE = re.compile(r'<a href="/tags/([^/]+)/">([^<]+)</a>')

DE_SPAN_BLOCK_RE = re.compile(r'<span><i class="fa-solid fa-tags"></i>.*?</span>', re.DOTALL)
DE_SPAN_LINE_RE = re.compile(r'^<span><i class="fa-solid fa-tags"></i>.*$', re.MULTILINE)


_JAHRHUNDERT_RE = re.compile(r"^(\d+)-jahrhundert$")


def label_for_term(term: str) -> str:
    slug = i18n_tags._slugify(term)

    m = _JAHRHUNDERT_RE.match(slug)
    if m:
        return f"{int(m.group(1))}. Jahrhundert"

    overrides: dict[str, str] = {
        "ki": "KI",
        "llm": "LLM",
        "dns": "DNS",
        "bernard-williams": "Bernard Williams",
        "williams": "Williams",
        "wittgenstein": "Wittgenstein",
        "nietzsche": "Nietzsche",
        "hume": "Hume",
        "hobbes": "Hobbes",
        "kant": "Kant",
        "krishnan": "Krishnan",
        "fricker": "Fricker",
        "craig": "Craig",
        "ki-ethik": "KI-Ethik",
        "erklaerbare-ki": "erklärbare KI",
        "ideologie-kritik": "Ideologiekritik",
        "begriffs-funktionen": "Begriffsfunktionen",
        "knowledge-first-erkenntnistheorie": "Knowledge-first Erkenntnistheorie",
        "genealogische-methode": "genealogische Methode",
        "methodologischer-pragmatismus": "methodologischer Pragmatismus",
    }
    if slug in overrides:
        return overrides[slug]

    stopwords = {
        "der",
        "des",
        "die",
        "das",
        "und",
        "oder",
        "von",
        "im",
        "in",
        "am",
        "auf",
        "an",
        "aus",
        "mit",
        "ohne",
        "ueber",
        "unter",
        "gegen",
        "bei",
        "zum",
        "zur",
        "vs",
        "fuer",
    }
    lowercase_adjectives = {
        "analytische",
        "britische",
        "kontinentale",
        "politische",
        "praktische",
        "theoretische",
        "pragmatische",
        "genealogische",
        "epistemische",
        "moralische",
        "moralisches",
        "mechanistische",
        "gemeinsames",
        "soziale",
        "sozial",
        "kulturelle",
        "kultureller",
    }

    def umlautify_ascii(word: str) -> str:
        if word == "metaethik":
            return word

        def repl(pattern: str, replacement: str, text: str) -> str:
            return re.sub(pattern, lambda m: f"{m.group(1)}{replacement}", text)

        # Prefer transliteration-style replacements, but avoid vowel+e sequences like "bioethik".
        word = repl(r"(^|[^aeiou])ae", "ä", word)
        word = repl(r"(^|[^aeiou])oe", "ö", word)
        word = repl(r"(^|[^aeiou])ue", "ü", word)
        return word

    def capitalize_word(word: str) -> str:
        if not word:
            return word
        return word[:1].upper() + word[1:]

    tokens = slug.split("-")
    out_words: list[str] = []
    for t in tokens:
        if t in ("ki", "llm", "dns"):
            out_words.append(t.upper())
            continue
        if t == "vs":
            out_words.append("vs.")
            continue
        word = umlautify_ascii(t)

        # Capitalization heuristics for German display labels
        if t in stopwords:
            out_words.append(word.lower())
            continue
        if word in ("KI", "LLM", "DNS"):
            out_words.append(word)
            continue
        if word.lower() in lowercase_adjectives:
            out_words.append(word.lower())
            continue
        out_words.append(capitalize_word(word))

    return " ".join(out_words)


def build_de_span(en_file_text: str) -> str:
    match = EN_SPAN_RE.search(en_file_text)
    if not match:
        raise ValueError("Could not find tags <span> in English entry.")

    span_html = match.group(0)
    en_slugs = [m.group(1) for m in EN_LINK_RE.finditer(span_html)]
    if not en_slugs:
        raise ValueError("Could not extract tag links from English span.")

    de_links: list[str] = []
    for en_slug in en_slugs:
        de_term = i18n_tags.translate_tag(en_slug, "de").term
        de_term = normalize_de_tags.normalize_tag(de_term)
        de_slug = i18n_tags.taxonomy_slug(de_term)
        de_label = label_for_term(de_term)
        de_links.append(f'<a href="/de/tags/{de_slug}/">{de_label}</a>')

    links_html = ", ".join(de_links)
    return f'<span><i class="fa-solid fa-tags"></i> {links_html}</span>'


def ensure_blank_line_before_download(text: str) -> str:
    return re.sub(r"(</span>)\n(<a class=\"download-link\")", r"\1\n\n\2", text)


def repair_backreference_artifacts(text: str) -> str:
    # Repair accidental literal backreferences introduced by an earlier buggy substitution.
    # In affected files, "\1" replaced the closing </span> and "\2" replaced '<a class="download-link"'.
    text = text.replace("\\1", "</span>")
    text = re.sub(r"\\2[ \t]+href=\"", "<a class=\"download-link\" href=\"", text)
    return text


def process_entry(en_path: Path, de_path: Path, dry_run: bool) -> bool:
    en_text = en_path.read_text(encoding="utf-8")
    de_text_original = de_path.read_text(encoding="utf-8")
    de_text = repair_backreference_artifacts(de_text_original)

    span = build_de_span(en_text)

    if ENTRY_TAGS_SHORTCODE in de_text:
        new_text = de_text.replace(ENTRY_TAGS_SHORTCODE, span)
    elif DE_SPAN_BLOCK_RE.search(de_text):
        new_text = DE_SPAN_BLOCK_RE.sub(span, de_text, count=1)
    elif DE_SPAN_LINE_RE.search(de_text):
        new_text = DE_SPAN_LINE_RE.sub(span, de_text, count=1)
    else:
        return False

    new_text = ensure_blank_line_before_download(new_text)

    if new_text == de_text_original:
        return False

    if not dry_run:
        de_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace {{< entry-tags >}} in DE entries with a 6-tag span mirroring the EN selection."
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes.")
    parser.add_argument("--entries", default="content/entries", help="Entries directory (default: content/entries).")
    args = parser.parse_args()

    entries_dir = Path(args.entries)
    changed: list[Path] = []

    for en_path in sorted(entries_dir.glob("*.md")):
        if en_path.name.endswith(".fr.md") or en_path.name.endswith(".de.md"):
            continue
        slug = en_path.stem
        de_path = entries_dir / f"{slug}.de.md"
        if not de_path.exists():
            continue
        if process_entry(en_path, de_path, dry_run=args.dry_run):
            changed.append(de_path)

    for p in changed:
        print(p)
    print(f"CHANGED_FILES {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
