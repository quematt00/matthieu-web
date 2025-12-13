#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


REWRITE: dict[str, str] = {
    # Page-level / common EN terms
    "AI": "ia",
    "ai": "ia",
    "ethics": "ethique",
    "politics": "politique",
    "normativity": "normativite",
    "genealogy": "genealogie",
    "paradigms": "paradigmes",
    "explanation": "explication",
    "history of philosophy": "histoire-de-la-philosophie",
    "conceptual history": "histoire-conceptuelle",
    # Core mixed tags / idiomatic FR
    "metaethics": "metaethique",
    "connectionism": "connexionnisme",
    "blame": "blâme",
    "systematicity": "systematicite",
    "systematicity-challenge": "defi-de-la-systematicite",
    "explainability": "explicabilite",
    "explainable-ia": "ia-explicable",
    "explainable-ai": "ia-explicable",
    "functions": "fonctions",
    "functionality": "fonctionnalite",
    "implementation": "mise-en-oeuvre",
    "decision-support": "aide-a-la-decision",
    "personalization": "personnalisation",
    "value-alignment": "alignement-des-valeurs",
    "valeur-alignment": "alignement-des-valeurs",
    # State of nature / social / language
    "etat-of-nature": "etat-de-nature",
    "social-cooperation": "cooperation-sociale",
    "language": "langage",
    "language-policy": "politique-linguistique",
    "language-games": "jeux-de-langage",
    # Liberalism of fear / internalism
    "liberalisme-of-fear": "liberalisme-de-la-peur",
    "internalism": "internalisme",
    # Debunking
    "debunking": "demystification",
    "genealogique-debunking": "demystification-genealogique",
    # Value / revaluation
    "revaluation-of-valeurs": "reevaluation-des-valeurs",
    "valeur-of-verite": "valeur-de-la-verite",
    "valeur-of-valeurs": "valeur-des-valeurs",
    "conflit-of-valeurs": "conflit-de-valeurs",
    # Reasons / causes
    "raisons-and-causes": "raisons-et-causes",
    "raisons-vs-causes": "raisons-contre-causes",
    "raisons-of-amour": "raisons-de-l-amour",
    "space-of-raisons": "espace-des-raisons",
    "chaine-of-raisons": "chaine-de-raisons",
    # Misc theory tags
    "theorie-of-esprit": "theorie-de-l-esprit",
    "philosophie-of-raisons": "philosophie-des-raisons",
    "philosophie-of-culture": "philosophie-de-la-culture",
    "phenomenologie-of-délibération": "phenomenologie-de-la-deliberation",
    "epistemologie-of-ia": "epistemologie-de-l-ia",
    "epistemique-limits": "limites-epistemiques",
    "epistemique-asymmetry": "asymetrie-epistemique",
    "metaphysique-of-action": "metaphysique-de-l-action",
    "causal-theorie-of-action": "theorie-causale-de-l-action",
    # AI / cog sci
    "mechanistic-interpretabilite": "interpretabilite-mecaniste",
    "latent-space": "espace-latent",
    "predictive-processing": "traitement-predictif",
    "predictive-compression": "compression-predictive",
    "ethique-and-the-limits-of-philosophie": "ethique-et-les-limites-de-la-philosophie",
    "ethics-and-the-limits-of-philosophy": "ethique-et-les-limites-de-la-philosophie",
    # Conceptual engineering cluster
    "conceptuel-engineering": "ingenierie-conceptuelle",
    "conceptual engineering": "ingenierie-conceptuelle",
    "conceptuel-ethique": "ethique-conceptuelle",
    "conceptuel-change": "changement-conceptuel",
    "conceptuel-disagreement": "desaccord-conceptuel",
    "conceptuel-integrity": "integrite-conceptuelle",
    "conceptuel-reverse-engineering": "analyse-conceptuelle-a-rebours",
    "conceptuel-histoire": "histoire-conceptuelle",
    "histoire-of-ideas": "histoire-des-idees",
    # Wittgenstein
    "late-wittgenstein": "wittgenstein-tardif",
    # Normalize a few known duplicates
    "conceptuel-pluralisme": "pluralisme-conceptuel",
    "conceptuel-évaluation": "evaluation-conceptuelle",
    # More idiomatic Francophone philosophy terms
    "analytique-philosophie": "philosophie-analytique",
    "politique-philosophie": "philosophie-politique",
    "continental-philosophie": "philosophie-continentale",
    "britannique-philosophie": "philosophie-britannique",
    "juridique-philosophie": "philosophie-du-droit",
    "meta-philosophie": "metaphilosophie",
    "moral-psychologie": "psychologie-morale",
    "moralite-system": "systeme-de-la-moralite",
    "pratique-raison": "raison-pratique",
    "valeur-theorie": "theorie-de-la-valeur",
    "politique-theorie": "theorie-politique",
    "ethique-theorie": "theorie-ethique",
    "action-theorie": "theorie-de-l-action",
    "non-ideal-theorie": "theorie-non-ideale",
    "critique-theorie": "theorie-critique",
    "critique-juridique-studies": "etudes-critiques-du-droit",
    "juridique-realisme": "realisme-juridique",
    "juridique-epistemologie": "epistemologie-juridique",
    "moderne-modern-philosophie": "philosophie-moderne",
    "ancienne-philosophie": "philosophie-antique",
    "stoic-ethique": "ethique-stoicienne",
    "patent-ethique": "ethique-des-brevets",
    "ethique-normative": "ethique-normative",
    "normatif-ethique": "ethique-normative",
    "nonmoral-valeur": "valeur-non-morale",
    "moralization": "moralisation",
    "moralism": "moralisme",
    "moral-raisons": "raisons-morales",
    "moral-prudence-dualism": "dualisme-moral-prudence",
    "moral-nonmoral-distinction": "distinction-moral-non-moral",
    "moral-advisors": "conseillers-moraux",
    "conceptuel-ethique-methodologie": "methodologie-de-l-ethique-conceptuelle",
    "epistemologie": "épistémologie",
    # Clean up remaining hybrid FR/EN compounds
    "pouvoir-asymmetry": "asymetrie-de-pouvoir",
    "structural-injustice": "injustice-structurelle",
    "personal-ia": "ia-personnalisee",
    "ia-gouvernance": "gouvernance-de-l-ia",
    "algorithmique-pouvoir": "pouvoir-algorithmique",
    "algorithmique-confiance": "confiance-algorithmique",
    "aspirationnel-valeurs": "valeurs-aspirationnelles",
    "dependance": "dépendance",
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
    parser = argparse.ArgumentParser(description="Normalize French tags in Hugo frontmatter.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes.")
    parser.add_argument("--root", default="content", help="Root directory to search (default: content).")
    args = parser.parse_args()

    root = Path(args.root)
    changed_files: list[Path] = []
    for path in sorted(root.rglob("*.fr.md")):
        if normalize_file(path, dry_run=args.dry_run):
            changed_files.append(path)

    for p in changed_files:
        print(p)
    print(f"CHANGED_FILES {len(changed_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
