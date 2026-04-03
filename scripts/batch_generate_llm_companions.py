#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIRS = (
    REPO_ROOT / "content" / "entries",
    REPO_ROOT / "content" / "books",
)
OUTPUT_DIR = REPO_ROOT / "static" / "llm" / "papers"
GENERATOR = REPO_ROOT / "scripts" / "generate_llm_text_companion.py"
SITE_BASE_URL = "https://www.matthieuqueloz.com"
SKIP_ENTRY_SUFFIXES = (".de.md", ".fr.md")
DOI_PATTERN = re.compile(r"(?:doi:|https?://doi\.org/)(10\.\S+?)(?=[)\]\s<]|$)", re.IGNORECASE)
PAGE_RANGE_PATTERN = re.compile(r"(?<!\d)(\d{1,4})\s*[–-]\s*\d{1,4}(?!\d)")
BAD_OUTPUT_MARKERS = (
    "Correspondence",
    "Email:",
    "Downloaded from ",
    "wileyonlinelibrary.com",
    "Page 1 of ",
    "Page 2 of ",
)
LAYOUT_HINT_MARKERS = (
    "Correspondence",
    "Email:",
    "Faculty of ",
    "School of ",
    "Department of ",
)
MANUAL_SLUG_OVERRIDES = {
    "needs of the mind": "needs-of-the-mind-how-aptic-normativity-can-guide-conceptual-adaptation",
    "why we care about understanding": "why-we-care-about-understanding-competence-through-predictive-compression",
    "explainability through systematicity": "explainability-through-systematicity-the-hard-systematicity-challenge-for-artificial-intelligence",
    "internalism from the ethnographic stance": "internalism-from-the-ethnographic-stance-from-self-indulgence-to-self-expression-and-corroborative-sense-making",
}


@dataclass
class EntryMetadata:
    path: Path
    section: str
    slug: str
    title: str
    citation: str
    doi: str
    pdf_url: str
    has_llm_companion: bool


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Expected YAML frontmatter delimited by ---")
    return match.group(1), match.group(2)


def extract_title(frontmatter: str) -> str:
    match = re.search(r'^title:\s*"(.+)"\s*$', frontmatter, flags=re.MULTILINE)
    if not match:
        raise ValueError("Missing title in frontmatter")
    return match.group(1)


def extract_first_citation_line(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and stripped != "<!--more-->":
            return stripped
    raise ValueError("Could not find citation line in body")


def extract_doi(text: str) -> str:
    match = DOI_PATTERN.search(text)
    return match.group(1).rstrip(".,);]") if match else ""


def extract_pdf_url(body: str) -> str:
    match = re.search(r'<a class="download-link" href="([^"]+)"', body)
    return match.group(1) if match else ""


def extract_start_page(citation: str) -> int:
    match = PAGE_RANGE_PATTERN.search(citation)
    return int(match.group(1)) if match else 1


def load_english_entries() -> list[EntryMetadata]:
    entries: list[EntryMetadata] = []
    for content_dir in CONTENT_DIRS:
        section = content_dir.name
        for path in sorted(content_dir.glob("*.md")):
            if path.name.endswith(SKIP_ENTRY_SUFFIXES):
                continue
            text = path.read_text(encoding="utf-8")
            frontmatter, body = split_frontmatter(text)
            title = extract_title(frontmatter)
            citation = extract_first_citation_line(body)
            doi = extract_doi(citation) or extract_doi(body)
            pdf_url = extract_pdf_url(body)
            slug = path.stem
            entries.append(
                EntryMetadata(
                    path=path,
                    section=section,
                    slug=slug,
                    title=title,
                    citation=citation,
                    doi=doi,
                    pdf_url=pdf_url,
                    has_llm_companion="llm_text_markdown:" in frontmatter,
                )
            )
    return entries


def build_entry_lookup(entries: list[EntryMetadata]) -> dict[str, EntryMetadata]:
    return {entry.slug: entry for entry in entries}


def match_entry(pdf_path: Path, entries: list[EntryMetadata], entry_lookup: dict[str, EntryMetadata]) -> tuple[EntryMetadata | None, float]:
    normalized_stem = normalize_text(pdf_path.stem)
    if normalized_stem in MANUAL_SLUG_OVERRIDES:
        slug = MANUAL_SLUG_OVERRIDES[normalized_stem]
        return entry_lookup.get(slug), 1.0

    candidates: list[tuple[float, EntryMetadata]] = []
    for entry in entries:
        normalized_title = normalize_text(entry.title)
        normalized_slug = normalize_text(entry.slug.replace("-", " "))
        if normalized_stem == normalized_title or normalized_stem == normalized_slug:
            return entry, 1.0
        if normalized_stem and (normalized_stem in normalized_title or normalized_title in normalized_stem):
            ratio = max(len(normalized_stem), len(normalized_title)) / max(1, min(len(normalized_stem), len(normalized_title)))
            score = min(0.99, 0.9 + 0.05 / ratio)
            candidates.append((score, entry))
            continue
        score = max(
            SequenceMatcher(None, normalized_stem, normalized_title).ratio(),
            SequenceMatcher(None, normalized_stem, normalized_slug).ratio(),
        )
        candidates.append((score, entry))

    if not candidates:
        return None, 0.0

    candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, best_entry = candidates[0]
    if best_score < 0.72:
        return None, best_score
    return best_entry, best_score


def run_text_command(args: list[str]) -> str:
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    return completed.stdout


def extract_first_page(pdf_path: Path, mode: str) -> str:
    args = ["pdftotext"]
    if mode == "layout":
        args.append("-layout")
    args.extend(["-f", "1", "-l", "1", str(pdf_path), "-"])
    return run_text_command(args)


def extract_pdf_doi(pdf_path: Path) -> str:
    output = run_text_command(["pdftotext", "-f", "1", "-l", "2", str(pdf_path), "-"])
    return extract_doi(output)


def line_exists(text: str, target: str) -> bool:
    return any(line.strip().casefold() == target.casefold() for line in text.splitlines())


def guess_generator_options(pdf_path: Path) -> tuple[str, str | None]:
    flow_page = extract_first_page(pdf_path, "flow")
    layout_page = extract_first_page(pdf_path, "layout")
    first_page_start_at = "Abstract" if line_exists(flow_page, "Abstract") or line_exists(layout_page, "Abstract") else None
    use_layout = False
    if any(marker in flow_page for marker in LAYOUT_HINT_MARKERS):
        use_layout = True
    if re.search(r"^\s*\d+\s*\|", layout_page, flags=re.MULTILINE):
        use_layout = True
    return ("layout" if use_layout else "flow"), first_page_start_at


def output_has_bad_markers(markdown_path: Path) -> bool:
    try:
        snippet = "\n".join(markdown_path.read_text(encoding="utf-8").splitlines()[:80])
    except FileNotFoundError:
        return True
    return any(marker in snippet for marker in BAD_OUTPUT_MARKERS)


def run_generator(
    entry: EntryMetadata,
    pdf_path: Path,
    output_stem: Path,
    mode: str,
    first_page_start_at: str | None,
    doi: str,
) -> None:
    args = [
        sys.executable,
        str(GENERATOR),
        str(pdf_path),
        str(output_stem),
        "--title",
        entry.title,
        "--author",
        "Matthieu Queloz",
        "--citation",
        entry.citation,
        "--doi",
        doi,
        "--start-page",
        str(extract_start_page(entry.citation)),
        "--entry-url",
        f"{SITE_BASE_URL}/{entry.section}/{entry.slug}/",
        "--pdf-url",
        entry.pdf_url,
        "--pdftotext-mode",
        mode,
    ]
    if first_page_start_at:
        args.extend(["--first-page-start-at", first_page_start_at])
    subprocess.run(args, check=True)


def insert_llm_frontmatter(entry_path: Path, slug: str) -> None:
    text = entry_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)
    if "llm_text_markdown:" in frontmatter and "llm_text_plain:" in frontmatter:
        return

    insert_lines = [
        f'llm_text_markdown: "/llm/papers/{slug}.md"',
        f'llm_text_plain: "/llm/papers/{slug}.txt"',
    ]
    lines = frontmatter.splitlines()
    if any(line.startswith("year:") for line in lines):
        index = next(i for i, line in enumerate(lines) if line.startswith("year:")) + 1
    else:
        index = next(i for i, line in enumerate(lines) if line.startswith("title:")) + 1
    lines[index:index] = insert_lines
    updated = "---\n" + "\n".join(lines) + "\n---\n" + body
    entry_path.write_text(updated, encoding="utf-8")


def process_pdf(pdf_path: Path, entries: list[EntryMetadata], entry_lookup: dict[str, EntryMetadata], force: bool) -> tuple[str, str]:
    if pdf_path.suffix.lower() != ".pdf":
        return "skipped", f"{pdf_path.name}: not a PDF"
    if not pdf_path.exists():
        return "missing", f"{pdf_path}: file not found"

    entry, score = match_entry(pdf_path, entries, entry_lookup)
    if entry is None:
        return "unmatched", f"{pdf_path.name}: no page match"
    if not entry.pdf_url:
        return "unmatched", f"{pdf_path.name}: page {entry.slug} has no PDF URL"

    output_stem = OUTPUT_DIR / entry.slug
    if entry.has_llm_companion and output_stem.with_suffix(".md").exists() and output_stem.with_suffix(".txt").exists() and not force:
        return "existing", f"{pdf_path.name}: already has companions via {entry.slug}"

    doi = entry.doi or extract_pdf_doi(pdf_path)
    mode, first_page_start_at = guess_generator_options(pdf_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_stem = Path(temp_dir) / entry.slug
        run_generator(entry, pdf_path, temp_stem, mode=mode, first_page_start_at=first_page_start_at, doi=doi)
        if mode == "flow" and output_has_bad_markers(temp_stem.with_suffix(".md")):
            run_generator(entry, pdf_path, temp_stem, mode="layout", first_page_start_at=first_page_start_at, doi=doi)

        output_stem.parent.mkdir(parents=True, exist_ok=True)
        output_stem.with_suffix(".md").write_text(temp_stem.with_suffix(".md").read_text(encoding="utf-8"), encoding="utf-8")
        output_stem.with_suffix(".txt").write_text(temp_stem.with_suffix(".txt").read_text(encoding="utf-8"), encoding="utf-8")

    insert_llm_frontmatter(entry.path, entry.slug)
    return "generated", f"{pdf_path.name}: {entry.slug} ({score:.2f})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-generate LLM companion files from PDF paths.")
    parser.add_argument("pdfs", nargs="+", type=Path)
    parser.add_argument("--force", action="store_true", help="Regenerate companions even when they already exist.")
    args = parser.parse_args()

    entries = load_english_entries()
    entry_lookup = build_entry_lookup(entries)
    summary: dict[str, list[str]] = {
        "generated": [],
        "existing": [],
        "unmatched": [],
        "missing": [],
        "skipped": [],
    }

    for pdf_path in args.pdfs:
        status, message = process_pdf(pdf_path, entries, entry_lookup, force=args.force)
        summary[status].append(message)
        print(message)

    print("\nSummary:")
    for key in ("generated", "existing", "unmatched", "missing", "skipped"):
        print(f"  {key}: {len(summary[key])}")


if __name__ == "__main__":
    main()
