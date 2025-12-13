#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

import i18n_tags
import normalize_fr_tags


ENTRY_TAGS_SHORTCODE = "{{< entry-tags >}}"

SPAN_RE = re.compile(r'<span><i class="fa-solid fa-tags"></i>\s*(.*?)</span>', re.DOTALL)
SPAN_BLOCK_RE = re.compile(r'<span><i class="fa-solid fa-tags"></i>.*?</span>', re.DOTALL)
LINK_RE = re.compile(r'<a href="/tags/([^/]+)/">([^<]+)</a>')


def label_for_term(term: str) -> str:
    slug = i18n_tags._slugify(term)

    overrides: dict[str, str] = {
        "ia": "IA",
        "llm": "LLM",
        "adn": "ADN",
        "explainable-ia": "IA explicable",
        "ia-explicable": "IA explicable",
        "internal-raisons": "raisons internes",
        "genealogie": "généalogie",
        "genealogies": "généalogies",
        "genealogique-methode": "méthode généalogique",
        "pragmatique-genealogie": "généalogie pragmatique",
        "ingenierie-conceptuelle": "ingénierie conceptuelle",
        "ethique": "éthique",
        "ethique-conceptuelle": "éthique conceptuelle",
        "metaethique": "métaéthique",
        "normativite": "normativité",
        "methodologie": "méthodologie",
        "rationalite": "rationalité",
        "systematicite": "systématicité",
        "asystematicite": "asystématicité",
        "verite": "vérité",
        "veracite": "véracité",
        "comprehension": "compréhension",
        "fonctionnalite": "fonctionnalité",
        "agentivite": "agentivité",
        "responsabilite": "responsabilité",
        "legitimite": "légitimité",
        "autorite": "autorité",
        "metaphilosophie": "métaphilosophie",
        "interpretabilite-mecaniste": "interprétabilité mécaniste",
        "bioethique": "bioéthique",
        "etat-de-nature": "état de nature",
        "systeme-de-la-moralite": "système de la moralité",
        "theorie-ethique": "théorie éthique",
        "theorie-de-l-action": "théorie de l’action",
        "action-explication": "action et explication",
        "commun-heritage": "héritage commun",
        "conceptuel-fonctions": "fonctions conceptuelles",
        "demystification-genealogique": "démystification généalogique",
        "ia-ethique": "IA éthique",
        "ideologie-critique": "critique de l’idéologie",
        "liberalisme": "libéralisme",
        "hermeneutique": "herméneutique",
        "culturel-critique": "critique culturelle",
        "philosophie-de-l-histoire": "philosophie de l’histoire",
        "philosophie-de-l-action": "philosophie de l’action",
        "philosophie-de-l-esprit": "philosophie de l’esprit",
        "hume": "Hume",
        "nietzsche": "Nietzsche",
        "foucault": "Foucault",
        "engel": "Engel",
        "rickert": "Rickert",
        "windelband": "Windelband",
        "wolf": "Wolf",
        "krishnan": "Krishnan",
        "craig": "Craig",
        "fricker": "Fricker",
        "williams": "Williams",
        "bernard-williams": "Bernard Williams",
    }
    if slug in overrides:
        return overrides[slug]

    label = term.replace("-", " ")

    # French typography / abbreviations
    label = re.sub(r"\\bia\\b", "IA", label)
    label = re.sub(r"\\bllm\\b", "LLM", label)
    label = re.sub(r"\\badn\\b", "ADN", label)

    # Contractions for l'IA / d'IA
    label = label.replace(" de l IA", " de l’IA").replace(" de l ia", " de l’IA")
    label = label.replace(" a l IA", " à l’IA").replace(" a l ia", " à l’IA")
    label = label.replace(" l IA", " l’IA").replace(" l ia", " l’IA")
    label = label.replace(" d IA", " d’IA").replace(" d ia", " d’IA")

    # Token-level accent fixes (fallback)
    token_map: dict[str, str] = {
        "ethique": "éthique",
        "metaethique": "métaéthique",
        "methodologie": "méthodologie",
        "methode": "méthode",
        "genealogie": "généalogie",
        "genealogique": "généalogique",
        "demystification": "démystification",
        "normativite": "normativité",
        "verite": "vérité",
        "veracite": "véracité",
        "epistemologie": "épistémologie",
        "metaphilosophie": "métaphilosophie",
        "agentivite": "agentivité",
        "responsabilite": "responsabilité",
        "legitimite": "légitimité",
        "autorite": "autorité",
        "systematicite": "systématicité",
        "asystematicite": "asystématicité",
        "interpretabilite": "interprétabilité",
        "mecaniste": "mécaniste",
        "bioethique": "bioéthique",
        "comprehension": "compréhension",
        "fonctionnalite": "fonctionnalité",
        "ingenierie": "ingénierie",
        "moralite": "moralité",
        "theorie": "théorie",
        "etat": "état",
        "siecle": "siècle",
        "rationalite": "rationalité",
    }

    def _fix_word(w: str) -> str:
        if any(ord(ch) > 127 for ch in w):
            return w
        lw = w.lower()
        return token_map.get(lw, w)

    label = " ".join(_fix_word(w) for w in label.split(" "))
    return label


def build_fr_span(en_file_text: str) -> str:
    match = SPAN_RE.search(en_file_text)
    if not match:
        raise ValueError("Could not find tags <span> in English entry.")

    span_html = match.group(0)
    en_slugs = [m.group(1) for m in LINK_RE.finditer(span_html)]
    if not en_slugs:
        raise ValueError("Could not extract tag links from English span.")

    fr_links: list[str] = []
    for en_slug in en_slugs:
        fr_term = i18n_tags.translate_tag(en_slug, "fr").term
        fr_term = normalize_fr_tags.normalize_tag(fr_term)
        fr_slug = i18n_tags.taxonomy_slug(fr_term)
        fr_label = label_for_term(fr_term)
        fr_links.append(f'<a href="/fr/tags/{fr_slug}/">{fr_label}</a>')

    links_html = ", ".join(fr_links)
    return f'<span><i class="fa-solid fa-tags"></i> {links_html}</span>'


def process_entry(en_path: Path, fr_path: Path, dry_run: bool) -> bool:
    en_text = en_path.read_text(encoding="utf-8")
    fr_text = fr_path.read_text(encoding="utf-8")

    span = build_fr_span(en_text)

    if ENTRY_TAGS_SHORTCODE in fr_text:
        new_text = fr_text.replace(ENTRY_TAGS_SHORTCODE, span)
    elif SPAN_BLOCK_RE.search(fr_text):
        new_text = SPAN_BLOCK_RE.sub(span, fr_text, count=1)
    else:
        return False

    if new_text == fr_text:
        return False

    if not dry_run:
        fr_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace {{< entry-tags >}} in FR entries with a 6-tag span mirroring the EN selection."
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
        fr_path = entries_dir / f"{slug}.fr.md"
        if not fr_path.exists():
            continue
        if process_entry(en_path, fr_path, dry_run=args.dry_run):
            changed.append(fr_path)

    for p in changed:
        print(p)
    print(f"CHANGED_FILES {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
