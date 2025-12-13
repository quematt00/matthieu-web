#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


REWRITE: dict[str, str] = {
    # Mixed EN/DE or EN-only (common offenders)
    "epistemisch-asymmetry": "epistemische-asymmetrie",
    "macht-asymmetry": "machtasymmetrie",
    "entscheidung-support": "entscheidungsunterstuetzung",
    "wert-alignment": "werteabstimmung",
    "personalization": "personalisierung",
    "language": "sprache",
    "language-policy": "sprachpolitik",
    "language-games": "sprachspiele",
    "staat-of-nature": "naturzustand",
    "state-of-nature": "naturzustand",
    "non-domination": "nichtbeherrschung",
    "liberalismus-of-fear": "liberalismus-der-furcht",
    "sozial-cooperation": "soziale-kooperation",
    "sozial-order": "soziale-ordnung",
    "sozial-ontology": "sozialontologie",
    "sozial-functions": "soziale-funktionen",
    "genealogy": "genealogie",
    "genealogisch-methode": "genealogische-methode",
    "systematicity": "systematizitaet",
    "systematicity-challenge": "systematizitaets-herausforderung",
    "predictive-compression": "praediktive-kompression",
    "latent-space": "latenter-raum",
    "space-of-gruende": "raum-der-gruende",
    "gruende-and-causes": "gruende-und-ursachen",
    "gruende-vs-causes": "gruende-vs-ursachen",
    "gruende-of-liebe": "gruende-der-liebe",
    "gruende-for-begriffe": "gruende-fuer-begriffe",
    "kette-of-gruende": "gruendekette",
    "theorie-of-geist": "geistestheorie",
    "metaphysik-of-handlung": "handlungsmetaphysik",
    "kausal-theorie-of-handlung": "kausaltheorie-des-handelns",
    "handlung-theorie": "handlungstheorie",
    "handlung-erklaerung": "handlungserklaerung",
    "philosophie-of-kultur": "kulturphilosophie",
    "philosophie-of-gruende": "philosophie-der-gruende",
    "phaenomenologie-of-deliberation": "phaenomenologie-der-deliberation",
    "non-ideal-theorie": "nicht-ideal-theorie",
    "konflikt-of-werte": "wertkonflikt",
    "revaluation-of-werte": "umwertung-der-werte",
    "wert-of-wahrheit": "wert-der-wahrheit",
    "wert-of-werte": "wert-der-werte",
    "dirty-hands": "schmutzige-haende",
    "will": "wille",
    "points": "zweck",
    "bedeutung-in-life": "sinn-im-leben",
    "expressive": "expressiv",
    "functions": "funktionen",
    "functionality": "funktionalitaet",
    "postwar": "nachkriegszeit",
    "predictive-processing": "praediktive-verarbeitung",
    "aspirational-werte": "aspirationale-werte",
    "structural-injustice": "strukturelle-ungerechtigkeit",
    "personal-ki": "personalisierte-ki",
    "ki-governance": "ki-regulierung",
    "knowledge-first-erkenntnistheorie": "wissen-zuerst-erkenntnistheorie",
    "thick-begriffe": "dichte-begriffe",
    "mechanistic-interpretierbarkeit": "mechanistische-interpretierbarkeit",
    "reactive-attitudes": "reaktive-einstellungen",
    "internal-gruende": "interne-gruende",
    "moralization": "moralisierung",
    "moralism": "moralismus",
    "nonmoral-wert": "nichtmoralischer-wert",
    "moral-system": "moralsystem",
    "moralisch-psychologie": "moralpsychologie",
    "moralisch-deliberation": "moralische-deliberation",
    "moralisch-advisors": "moralberater",
    "moralisch-prudence-dualism": "moral-klugheit-dualismus",
    "moralisch-nonmoral-distinction": "unterscheidung-moralisch-nichtmoralisch",
    "moralisch-gruende": "moralische-gruende",
    "praktisch-grund": "praktische-gruende",
    "praktisch-origins": "praktische-urspruenge",
    "praktisch-deliberation": "praktische-deliberation",
    "politisch-theorie": "politische-theorie",
    "politisch-realismus": "politischer-realismus",
    "politisch-werte": "politische-werte",
    "politisch-kontext": "politischer-kontext",
    "ethisch-theorie": "ethiktheorie",
    "epistemisch-limits": "epistemische-grenzen",
    "epistemisch-wert": "epistemischer-wert",
    "epistemisch-vertrauen": "epistemisches-vertrauen",
    "algorithmisch-macht": "algorithmische-macht",
    "algorithmisch-vertrauen": "algorithmisches-vertrauen",
    "humanistisch-discipline": "humanistische-disziplin",
    "ethnographisch-stance": "ethnographischer-standpunkt",
    "kritisch-theorie": "kritische-theorie",
    "kritisch-rechtlich-studies": "kritische-rechtswissenschaft",
    "genealogisch-debunking": "genealogische-entlarvung",
    "debunking": "entlarvung",
    "methodological-pragmatismus": "methodologischer-pragmatismus",
    # Conceptual engineering / related (German compounds)
    "begrifflich-engineering": "begriffsengineering",
    "conceptual engineering": "begriffsengineering",
    "begrifflich-change": "begriffswandel",
    "begrifflich-geschichte": "begriffsgeschichte",
    "begrifflich-functions": "begriffs-funktionen",
    "begrifflich-disagreement": "begriffsstreit",
    "begrifflich-pluralismus": "begriffspluralismus",
    "begrifflich-integrity": "begriffsintegritaet",
    "begrifflich-ethik": "begriffsethik",
    "begrifflich-ethik-methodologie": "begriffsethik-methodologie",
    "begrifflich-bewertung": "begriffsbewertung",
    "begriff-bewertung": "begriffsbewertung",
    "begrifflich-anpassung": "begriffsanpassung",
    "begrifflich-revision": "begriffsrevision",
    "begrifflich-uptake": "begriffsaufnahme",
    "begrifflich-testing": "begriffstest",
    "begrifflich-staerke": "begriffsstaerke",
    "begriff-legitimitaet": "begriffslegitimitaet",
    "politisch-begriffe": "politische-begriffe",
    "epistemisch-begriffe": "epistemische-begriffe",
    "begrifflich-reverse-engineering": "begriffliche-rueckwaertsanalyse",
    "geschichte-of-ideas": "ideengeschichte",
    # More idiomatic German (avoid adjective stems / hybrids)
    "analytisch-philosophie": "analytische-philosophie",
    "britisch-philosophie": "britische-philosophie",
    "politisch-philosophie": "politische-philosophie",
    "rechtlich-philosophie": "rechtsphilosophie",
    "meta-philosophie": "metaphilosophie",
    "metaethics": "metaethik",
    "continental-philosophie": "kontinentalphilosophie",
    "frueh-modern-philosophie": "fruehe-neuzeit",
    "fruehneuzeitsphilosophie": "fruehe-neuzeit",
    "stoic-ethik": "stoische-ethik",
    "patent-ethik": "patentethik",
    "erkenntnistheorie-of-ki": "erkenntnistheorie-der-ki",
    "ethik-and-the-limits-of-philosophie": "ethik-und-die-grenzen-der-philosophie",
    "ethics-and-the-limits-of-philosophy": "ethik-und-die-grenzen-der-philosophie",
    "wert-change": "wertewandel",
    "pragmatisch-genealogie": "pragmatische-genealogie",
    "Williams": "williams",
    # Page-level tag phrases (inline arrays)
    "ethics": "ethik",
    "politics": "politik",
    "normativity": "normativitaet",
    "AI": "KI",
    "history of philosophy": "geschichte-der-philosophie",
    "conceptual history": "begriffsgeschichte",
    "connectionism": "konnektionismus",
    "explainability": "erklaerbarkeit",
    "explainable-ki": "erklaerbare-ki",
    "explainable-ai": "erklaerbare-ki",
    "authority": "autoritaet",
    "paradigms": "paradigmen",
    "explanation": "erklaerung",
    "internalism": "internalismus",
    "genealogies": "genealogien",
    "gemeinsam-heritage": "gemeinsames-erbe",
}


def normalize_tag(tag: str) -> str:
    tag = tag.strip()
    return REWRITE.get(tag, tag)


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def split_frontmatter(lines: list[str]) -> tuple[list[str], list[str], list[str]] | None:
    if not lines:
        return None
    if lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return (lines[:1], lines[1:i], lines[i:])  # leading '---', fm, rest starting with closing '---'
    return None


def parse_inline_array(array_text: str) -> list[str]:
    # Minimal CSV-like parser for ["a", "b"] or ['a','b'].
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


def normalize_frontmatter_tags(fm_lines: list[str]) -> tuple[list[str], bool]:
    changed = False
    out: list[str] = []
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]

        m_inline = re.match(r"^tags:\s*(\[.*\])\s*$", line.strip())
        if m_inline:
            array = m_inline.group(1).strip()
            inner = array[1:-1].strip()
            items = parse_inline_array(inner) if inner else []
            items = [normalize_tag(t) for t in items]
            items = dedupe_preserve_order(items)
            new_line = f"tags: {format_inline_array(items)}\n"
            if new_line != line:
                changed = True
            out.append(new_line)
            i += 1
            continue

        if line.strip() == "tags:":
            out.append(line)
            i += 1
            items: list[str] = []
            item_indent = None
            while i < len(fm_lines):
                l2 = fm_lines[i]
                if re.match(r"^\w", l2):
                    break
                m_item = re.match(r"^(\s*)-\s*(.*?)\s*$", l2.rstrip("\n"))
                if m_item:
                    item_indent = item_indent or m_item.group(1)
                    raw = m_item.group(2).strip()
                    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                        raw = raw[1:-1]
                    items.append(raw)
                i += 1

            new_items = [normalize_tag(t) for t in items]
            new_items = dedupe_preserve_order(new_items)
            if new_items != items:
                changed = True

            indent = item_indent if item_indent is not None else "  "
            for t in new_items:
                out.append(f"{indent}- \"{t}\"\n")
            continue

        out.append(line)
        i += 1
    return out, changed


def normalize_file(path: Path, dry_run: bool) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    parts = split_frontmatter(lines)
    if parts is None:
        return False
    head, fm_lines, tail = parts
    new_fm, changed = normalize_frontmatter_tags(fm_lines)
    if not changed:
        return False
    new_text = "".join(head + new_fm + tail)
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize German tags in Hugo frontmatter.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes.")
    parser.add_argument("--root", default="content", help="Root directory to search (default: content).")
    args = parser.parse_args()

    root = Path(args.root)
    changed_files: list[Path] = []
    for path in sorted(root.rglob("*.de.md")):
        if normalize_file(path, dry_run=args.dry_run):
            changed_files.append(path)

    for p in changed_files:
        print(p)
    print(f"CHANGED_FILES {len(changed_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
