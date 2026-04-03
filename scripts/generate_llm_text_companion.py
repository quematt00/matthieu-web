#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import statistics
import subprocess
import unicodedata
from pathlib import Path

DASH_CHARS = "—―–-"
DASH_CLASS = re.escape(DASH_CHARS)
HEADING_STOPWORDS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with"}


def parse_mapping(values: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Expected KEY=VALUE mapping, got: {value}")
        key, mapped = value.split("=", 1)
        mapping[key] = mapped
    return mapping


def run_text_command(args: list[str]) -> str:
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    return completed.stdout


def normalize_ligatures(text: str) -> str:
    return (
        text.replace("ﬀ", "ff")
        .replace("ﬁ", "fi")
        .replace("ﬂ", "fl")
        .replace("ﬃ", "ffi")
        .replace("ﬄ", "ffl")
        .replace("ﬅ", "ft")
        .replace("ﬆ", "st")
    )


def pdf_page_count(pdf_path: Path) -> int:
    output = run_text_command(["pdfinfo", str(pdf_path)])
    match = re.search(r"^Pages:\s+(\d+)$", output, flags=re.MULTILINE)
    if not match:
        raise SystemExit("Could not determine PDF page count via pdfinfo.")
    return int(match.group(1))


def extract_page(pdf_path: Path, page_number: int, mode: str) -> str:
    args = ["pdftotext"]
    if mode == "layout":
        args.append("-layout")
    args.extend(
        [
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            str(pdf_path),
            "-",
        ]
    )
    return run_text_command(args)


def normalize_line(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\x0c", "")
    text = normalize_ligatures(text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)
    text = re.sub(r"^[\ue000-\uf8ff-]+\s*", "", text)
    return text.rstrip()


def normalize_paragraph(text: str, replacements: dict[str, str]) -> str:
    text = unicodedata.normalize("NFC", text)
    text = normalize_ligatures(text)
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)
    text = re.sub(r"^\*{3,}\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def matches_line(text: str, target: str | None) -> bool:
    return bool(target) and text.casefold() == target.casefold()


def compact_heading_key(text: str) -> str:
    return re.sub(r"\s+", "", text).upper()


def looks_like_author_header(text: str, author: str) -> bool:
    if matches_line(text, author):
        return True

    author_parts = author.split()
    if len(author_parts) < 2:
        return False

    surname = author_parts[-1].strip(",")
    given_names = [part.strip(",") for part in author_parts[:-1] if part.strip(",")]
    initials = ". ".join(part[0].upper() for part in given_names if part[:1].isalpha())
    if not initials:
        return False
    return text.casefold() == f"{initials}. {surname}".casefold()


def looks_like_title_header(text: str, title: str) -> bool:
    stripped = text.strip()
    if matches_line(stripped, title):
        return True

    for ellipsis in ("…", "..."):
        if stripped.endswith(ellipsis):
            prefix = stripped[: -len(ellipsis)].strip()
            if len(prefix) >= min(24, max(12, len(title) // 3)) and title.casefold().startswith(prefix.casefold()):
                return True
    return False


def looks_like_numbered_heading_core(number_text: str, heading_text: str) -> bool:
    if int(number_text) > 20:
        return False
    if len(heading_text) > 120 or heading_text.endswith((".", ";", ":")):
        return False
    if "Page " in heading_text and " of " in heading_text:
        return False

    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9'’\-]*\??", heading_text)
    if not words or len(words) > 18:
        return False

    significant_words = [
        word
        for word in words
        if not word.isdigit() and word.casefold().rstrip("?") not in HEADING_STOPWORDS
    ]
    if not significant_words:
        return False

    if len(significant_words) == 1 and len(significant_words[0].rstrip("?")) <= 4:
        return False

    title_case_words = 0
    for word in significant_words:
        bare = word.rstrip("?")
        if bare[:1].isupper() or bare.isupper():
            title_case_words += 1

    return title_case_words / len(significant_words) >= 0.75


def looks_like_numbered_heading(stripped: str) -> bool:
    match = re.fullmatch(r"([0-9]{1,2})\.\s+(.+)", stripped)
    if not match:
        return False

    return looks_like_numbered_heading_core(match.group(1), match.group(2).strip())


def looks_like_spaced_numbered_heading(stripped: str) -> bool:
    match = re.fullmatch(r"([0-9]{1,2})\s+(.+)", stripped)
    if not match:
        return False

    return looks_like_numbered_heading_core(match.group(1), match.group(2).strip())


def looks_like_decimal_heading(stripped: str) -> bool:
    match = re.fullmatch(r"([0-9]{1,2}(?:\.[0-9]{1,2})+)\s+(.+)", stripped)
    if not match:
        return False

    number_text = match.group(1).split(".", 1)[0]
    return looks_like_numbered_heading_core(number_text, match.group(2).strip())


def looks_like_barred_numbered_heading(stripped: str) -> bool:
    return bool(re.fullmatch(r"[0-9]{1,2}\s*\|\s*.+", stripped))


def looks_like_garbled_running_header(stripped: str) -> bool:
    if len(stripped) < 8:
        return False

    letter_count = sum(char.isalpha() for char in stripped)
    weird_count = sum(char.isdigit() or char in "&@/\\=<>;:,'`()*[]{}" for char in stripped)
    if letter_count > max(4, len(stripped) // 4):
        return False
    return weird_count >= max(5, len(stripped) // 4)


def looks_like_short_uppercase_header(stripped: str) -> bool:
    if len(stripped) > 48:
        return False
    letters = [char for char in stripped if char.isalpha()]
    if not letters:
        return False
    return all(char.isupper() for char in letters)


def looks_like_layout_running_header(stripped: str) -> bool:
    if len(stripped) > 90 or not re.search(r"\d", stripped):
        return False
    letters = [char for char in stripped if char.isalpha()]
    if len(letters) < 5:
        return False
    uppercase_letters = sum(char.isupper() for char in letters)
    return uppercase_letters / len(letters) >= 0.85


def count_private_use_chars(text: str) -> int:
    return sum(unicodedata.category(char) == "Co" for char in text)


def looks_like_private_use_running_header(stripped: str) -> bool:
    if count_private_use_chars(stripped) < 4:
        return False
    visible = [char for char in stripped if not char.isspace()]
    if not visible:
        return False
    return count_private_use_chars(stripped) / len(visible) >= 0.45


def looks_like_footer_citation_line(stripped: str, title: str, author: str) -> bool:
    if title in stripped and author in stripped:
        return True
    if "Oxford University Press" in stripped and "DOI:" in stripped:
        return True
    if "©" in stripped and ("DOI:" in stripped or "DOT:" in stripped or "10.1093/" in stripped):
        return True
    return False


BOILERPLATE_MARKERS = (
    "Acknowledgements",
    "Acknowledgments",
    "Authors’ Contributions",
    "Authors' Contributions",
    "Author Contributions",
    "Funding",
    "Data Availability",
    "Declarations",
    "Ethics Approval",
    "Consent for Publication",
    "Competing interests",
    "Competing Interests",
    "Open Access This article",
)


def clean_page_lines(
    raw_page: str,
    title: str,
    author: str,
    is_first_page: bool,
    mode: str,
    first_page_start_at: str | None = None,
    first_page_stop_before: str | None = None,
) -> list[str]:
    cleaned: list[str] = []
    footer_snippets = (
        "Creative Commons Attribution-NonCommercial License",
        "journals.permissions@oup.com",
        "non-commercial re-use",
        "commercial re-use",
    )
    keep_from_abstract = mode == "flow" and is_first_page and not first_page_start_at
    abstract_seen = False
    start_marker_seen = not (is_first_page and first_page_start_at)
    before_main_body_heading = is_first_page
    for raw_line in raw_page.splitlines():
        line = normalize_line(raw_line)
        line = re.sub(
            r"^(?:\d{4}\s+)?Synthese\s+\(\d{4}\)\s+\d+:\d+[-–]\d+(?:\s+\d{4})?\s*",
            "",
            line,
        )
        line = re.sub(
            r"^\d{4}\s+Synthese\s+\(\d{4}\)\s+\d+:\d+[-–]\d+\s*$",
            "",
            line,
        )
        line = re.sub(r"^(?:\d{1,3}\s+)?[A-Z][A-Z\s&.'’/-]{3,}\s{2,}(?=[A-ZÀ-ÖØ-öø-ÿa-z“\"(])", "", line)
        line = re.sub(r"\s{2,}[A-Z][A-Z\s&.'’/-]{3,}\s+\d{1,3}$", "", line)
        line = re.sub(r"^[A-Z]\.\s+[A-Za-zÀ-ÖØ-öø-ÿ'’\-]+\s*\(\d{4}\)\d+:\d+\s*", "", line)
        line = re.sub(r"^(?:[A-Z][A-Z'’\-]*\s+){2,5}(?=[a-z“\"(])", "", line)
        if "Page " in line and " of " in line:
            page_header_match = re.match(r"^.*?Page\s+\d+\s+of\s+\d+\s+\d+\s+", line)
            if page_header_match:
                line = line[page_header_match.end() :]
        first_alpha_match = re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", line)
        prefix = line[: first_alpha_match.start()] if first_alpha_match else ""
        if (
            first_alpha_match
            and sum(not char.isspace() for char in prefix) >= 3
            and not re.search(r"\d", prefix)
        ):
            line = line[first_alpha_match.start() :]
        stripped = line.strip()

        if not stripped:
            if mode == "flow" and cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue

        if is_first_page and (
            stripped.lower().startswith(("1. department of", "department of"))
            or stripped == "Switzerland"
        ):
            continue

        if mode == "layout" and re.match(r"^\d{1,2}\s+[A-Za-zÀ-ÖØ-öø-ÿ]", stripped) and not looks_like_spaced_numbered_heading(stripped):
            line = re.sub(r"^\d{1,2}\s+", "", line, count=1)
            stripped = line.strip()

        if line.endswith(" 123"):
            line = re.sub(r"\s+123$", "", line)
            stripped = line.strip()

        start_marker_match = None
        if is_first_page and first_page_start_at:
            start_marker_match = re.search(
                rf"(?:^|\s){re.escape(first_page_start_at)}(?:\b|:)?\s*(.*)$",
                stripped,
                flags=re.IGNORECASE,
            )
        if start_marker_match:
            start_marker_seen = True
            cleaned.append(first_page_start_at)
            remainder = start_marker_match.group(1).strip(" :")
            if remainder:
                if is_first_page and re.search(r"\bKeywords\b", remainder):
                    before, _, keyword_tail = remainder.partition("Keywords")
                    before = before.rstrip(" .")
                    keyword_tail = re.sub(
                        rf"\bB\s+{re.escape(author)}\s*$",
                        "",
                        keyword_tail,
                        flags=re.IGNORECASE,
                    ).strip(" .:")
                    if before:
                        cleaned.append(before + ".")
                    if keyword_tail:
                        cleaned.append(f"Keywords: {keyword_tail}")
                else:
                    cleaned.append(remainder)
            if first_page_start_at.casefold() == "abstract":
                abstract_seen = True
            continue

        if is_first_page and matches_line(stripped, first_page_stop_before):
            break

        if before_main_body_heading and (
            looks_like_barred_numbered_heading(stripped)
            or looks_like_numbered_heading(stripped)
            or looks_like_spaced_numbered_heading(stripped)
        ):
            before_main_body_heading = False

        if not start_marker_seen:
            if matches_line(stripped, first_page_start_at):
                start_marker_seen = True
                cleaned.append(first_page_start_at or stripped)
            continue

        if keep_from_abstract and not abstract_seen:
            if stripped.lower() == "abstract":
                abstract_seen = True
                cleaned.append("Abstract")
            continue

        if "Downloaded from " in stripped:
            continue

        if stripped.startswith(("http://", "https://")):
            continue

        if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", stripped):
            continue

        if len(stripped) <= 160 and any(
            marker in stripped
            for marker in (
                "Institute of Philosophy",
                "University of Bern",
                "Laenggassstrasse",
                "Bern 3012",
            )
        ):
            continue

        if "OUP CORRECTED AUTOPAGE PROOFS" in stripped or "OUP UNCORRECTED PROOF" in stripped:
            continue

        if stripped in {"This content downloaded from", "All use subject to https://about.jstor.org/terms", "x"}:
            continue

        if looks_like_private_use_running_header(stripped):
            continue

        if looks_like_footer_citation_line(stripped, title, author):
            continue

        if "wileyonlinelibrary.com/journal/" in stripped:
            continue

        if looks_like_garbled_running_header(stripped):
            continue

        if stripped in {"K", "J", "k", "j"}:
            continue

        if "Page " in stripped and " of " in stripped:
            continue

        if re.fullmatch(r"[A-Z]\.\s+[A-Za-zÀ-ÖØ-öø-ÿ'’\-]+\s*\(\d{4}\).+", stripped):
            continue

        if stripped.startswith("How to cite this article:"):
            break

        if stripped.startswith("This is an open access article"):
            break

        if stripped.startswith("Publisher’s Note") or stripped.startswith("Publisher's Note"):
            break

        if re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} on .+ UTC", stripped):
            continue

        if re.fullmatch(r"\d{2}\.\d{2}\.\d{2},\s*\d{2}:\d{2}", stripped):
            continue

        if re.fullmatch(r"(?:\d{1,3}\s+[A-Z][A-Z\s&.'’/-]{3,}|[A-Z][A-Z\s&.'’/-]{3,}\s+\d{1,3})", stripped):
            continue

        if mode == "flow" and " | " in stripped and any(label in stripped for label in ("Essay", "Essays", "Magazine", "Review")):
            continue

        if mode == "layout" and not is_first_page and looks_like_short_uppercase_header(stripped):
            continue

        if mode == "layout" and not is_first_page and looks_like_layout_running_header(stripped):
            continue

        if mode == "flow" and (
            re.fullmatch(r"\d+\s*/\s*[A-Z][A-Z\s/]+", stripped)
            or re.fullmatch(r"[A-Z][A-Z\s/]+\s*/\s*\d+", stripped)
            or "philosophers’ imprint" in stripped.casefold()
            or re.fullmatch(rf"[{DASH_CLASS}\s]*\d+[{DASH_CLASS}\s]*", stripped)
            or stripped.casefold().startswith("vol. ")
            or stripped.startswith("Page ") and " of " in stripped
            or stripped.casefold().startswith("vol.:")
            or looks_like_author_header(stripped, author)
            or looks_like_title_header(stripped, title)
            or looks_like_short_uppercase_header(stripped)
        ):
            continue

        if is_first_page and (
            stripped.startswith("Received:")
            or stripped.startswith("Accepted:")
            or stripped.startswith("DOI:")
            or stripped == "ORIGINAL ARTICLE"
            or stripped == "COMMENTARY"
            or re.fullmatch(r".+\(\d{4}\)\s+\d+:\d+", stripped)
            or re.fullmatch(r".+\(\d{4}\)\s+\d+", stripped)
            or stripped.startswith("The Monist,")
            or stripped.startswith("https://doi.org/")
            or stripped == "Article"
            or matches_line(stripped, title)
            or stripped == f"{author}*"
            or looks_like_author_header(stripped, author)
            or (mode == "layout" and "|" in stripped and re.search(r"\d", stripped) and not looks_like_barred_numbered_heading(stripped))
            or stripped == "*University of Oxford, UK"
            or stripped.startswith("Copyright ")
            or stripped.startswith("©")
            or any(snippet in stripped for snippet in footer_snippets)
        ):
            continue

        if is_first_page and before_main_body_heading and (
            stripped.startswith(("Faculty of ", "Department of ", "Correspondence", "Email:"))
            or (
                len(stripped) <= 120
                and any(marker in stripped for marker in ("University of", "College", "School of", "Faculty of"))
            )
            or matches_line(stripped, f"by {author}")
            or "Courtesy of" in stripped
            or stripped.startswith(f"{author} is ")
            or stripped.startswith(f"{author} was ")
        ):
            continue

        if title in stripped and re.search(r"\b\d{3}\b", stripped):
            continue

        if stripped.isdigit() and (mode == "flow" or (is_first_page and before_main_body_heading)):
            continue

        if stripped.isdigit() and len(stripped) <= 3:
            continue

        if (
            stripped == "ORCID"
            or "orcid.org/" in stripped
            or "[Correction added on " in stripped
            or "Wiley-Blackwell apologizes for this error." in stripped
            or "all subsequent endnote pointers have been" in stripped
        ):
            continue

        if matches_line(stripped, title):
            continue

        if " Keywords:" in line and not stripped.startswith("Keywords:"):
            before_keywords, keywords = line.split(" Keywords:", 1)
            before_keywords = before_keywords.rstrip()
            if before_keywords:
                cleaned.append(before_keywords)
            cleaned.append(f"Keywords: {keywords.strip()}")
            continue

        cleaned.append(line)

    return cleaned


def is_heading(stripped: str, heading_map: dict[str, str]) -> bool:
    compact = compact_heading_key(stripped)
    return compact in {"ABSTRACT", "NOTES", "ENDNOTES", "REFERENCES", "ACKNOWLEDGEMENTS", "ACKNOWLEDGMENTS"} or stripped in heading_map or compact in heading_map or bool(
        re.fullmatch(
            r"[0-9]+\s*\.\s*[A-Z][A-Z\s,]+",
            stripped,
        )
    ) or looks_like_numbered_heading(stripped) or looks_like_spaced_numbered_heading(stripped) or looks_like_decimal_heading(stripped) or looks_like_barred_numbered_heading(stripped)


def normalize_heading_text(stripped: str, heading_map: dict[str, str]) -> str:
    stripped = re.sub(r"\s*\|\s*", " ", stripped)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    if stripped in heading_map:
        return heading_map[stripped]

    compact = compact_heading_key(stripped)
    if compact in heading_map:
        return heading_map[compact]
    if compact == "ABSTRACT":
        return "Abstract"
    if compact == "NOTES":
        return "Notes"
    if compact == "ENDNOTES":
        return "Notes"
    if compact == "REFERENCES":
        return "References"
    if compact in {"ACKNOWLEDGEMENTS", "ACKNOWLEDGMENTS"}:
        return "Acknowledgements"
    spaced_match = re.fullmatch(r"([0-9]{1,2})\s+(.+)", stripped)
    if spaced_match and looks_like_spaced_numbered_heading(stripped):
        return f"{spaced_match.group(1)}. {spaced_match.group(2).strip()}"
    return stripped


def is_reference_section_name(text: str) -> bool:
    return text.casefold() in {"references", "bibliography", "works cited"}


def is_reference_heading(stripped: str, heading_map: dict[str, str]) -> bool:
    return is_reference_section_name(normalize_heading_text(stripped, heading_map))


def append_piece(parts: list[str], piece: str) -> None:
    if not parts:
        parts.append(piece)
        return

    previous = parts[-1]
    if previous.endswith("-") and piece[:1].islower():
        parts[-1] = previous[:-1] + piece
        return

    parts.append(piece)


def looks_like_heading_fragment(stripped: str) -> bool:
    if len(stripped) > 60 or re.search(r"[.!?]$", stripped):
        return False
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9'’\-]*", stripped)
    if not words or len(words) > 10:
        return False
    significant_words = [word for word in words if word.casefold() not in HEADING_STOPWORDS]
    if not significant_words:
        significant_words = words
    title_case_words = sum(word[:1].isupper() or word.isupper() for word in significant_words)
    return title_case_words / len(significant_words) >= 0.75


def merge_layout_heading_fragments(lines: list[str], heading_map: dict[str, str]) -> list[str]:
    merged: list[str] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.isdigit():
            next_index = index + 1
            fragments: list[str] = []
            while next_index < len(lines):
                candidate = lines[next_index].strip()
                if not candidate:
                    next_index += 1
                    continue
                if is_heading(candidate, heading_map):
                    break
                if len(fragments) < 3 and looks_like_heading_fragment(candidate):
                    fragments.append(candidate)
                    next_index += 1
                    continue
                break
            if fragments:
                combined = f"{stripped} {' '.join(fragments)}"
                if is_heading(combined, heading_map):
                    merged.append(combined)
                    index = next_index
                    continue
        merged.append(lines[index])
        index += 1
    return merged


def flush_paragraph(blocks: list[tuple[str, str]], parts: list[str], replacements: dict[str, str]) -> None:
    if not parts:
        return
    paragraph = ""
    for piece in parts:
        if not paragraph:
            paragraph = piece
        elif paragraph.endswith("-") and piece[:1].islower():
            paragraph = paragraph[:-1] + piece
        else:
            paragraph = f"{paragraph} {piece}"
    paragraph = normalize_paragraph(paragraph, replacements)
    if paragraph:
        blocks.append(("paragraph", paragraph))
    parts.clear()


def page_blocks_layout(
    raw_page: str,
    title: str,
    author: str,
    heading_map: dict[str, str],
    replacements: dict[str, str],
    is_first_page: bool,
    initial_section: str = "body",
    first_page_start_at: str | None = None,
    first_page_stop_before: str | None = None,
) -> tuple[list[tuple[str, str]], str]:
    lines = clean_page_lines(
        raw_page,
        title,
        author,
        is_first_page,
        mode="layout",
        first_page_start_at=first_page_start_at,
        first_page_stop_before=first_page_stop_before,
    )
    lines = merge_layout_heading_fragments(lines, heading_map)
    blocks: list[tuple[str, str]] = []
    paragraph_parts: list[str] = []
    in_references = initial_section == "references"
    in_notes = initial_section == "notes"
    previous_line_indented = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.isdigit():
            next_nonempty = ""
            for candidate in lines[index + 1 :]:
                if candidate.strip():
                    next_nonempty = candidate.strip()
                    break
            if next_nonempty and is_heading(next_nonempty, heading_map):
                continue

        if is_heading(stripped, heading_map):
            flush_paragraph(blocks, paragraph_parts, replacements)
            heading_text = normalize_heading_text(stripped, heading_map)
            blocks.append(("heading", heading_text))
            if is_reference_section_name(heading_text):
                in_references = True
                in_notes = False
            elif heading_text.lower() == "notes":
                in_notes = True
                in_references = False
            else:
                in_notes = False
                in_references = False
            continue

        if in_references:
            if line.startswith(" ") and paragraph_parts:
                append_piece(paragraph_parts, stripped)
            else:
                flush_paragraph(blocks, paragraph_parts, replacements)
                paragraph_parts.append(stripped)
            continue

        if in_notes:
            note_match = re.fullmatch(r"(\d+)\.?", stripped)
            if note_match:
                flush_paragraph(blocks, paragraph_parts, replacements)
                paragraph_parts.append(f"{note_match.group(1)}.")
            else:
                append_piece(paragraph_parts, stripped)
            previous_line_indented = line.startswith("    ")
            continue

        is_indented = line.startswith("    ")
        if is_indented and paragraph_parts and not previous_line_indented:
            flush_paragraph(blocks, paragraph_parts, replacements)
            paragraph_parts.append(stripped)
            previous_line_indented = is_indented
            continue

        if not paragraph_parts:
            paragraph_parts.append(stripped)
            previous_line_indented = is_indented
            continue

        append_piece(paragraph_parts, stripped)
        previous_line_indented = is_indented

    flush_paragraph(blocks, paragraph_parts, replacements)
    blocks = reorder_backmatter_columns(blocks)
    blocks = normalize_reference_blocks(blocks)
    blocks = strip_journal_boilerplate_blocks(blocks)
    return blocks, final_section_name(in_notes, in_references)


def repair_drop_caps(lines: list[str]) -> list[str]:
    repaired: list[str] = []
    index = 0
    while index < len(lines):
        current = lines[index].strip()
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        next_line = lines[next_index].strip() if next_index < len(lines) else ""
        if len(current) == 1 and current.isupper() and next_line[:1].islower():
            repaired.append(f"{current}{next_line}")
            index = next_index + 1
            continue
        repaired.append(lines[index])
        index += 1
    return repaired


REFERENCE_ENTRY_LABEL_PATTERN = r"(?:\d{4}[a-z]?\.|Manuscript\.|\((?:\d{4}[a-z]?|[Ff]orthcoming(?:-[a-z])?)(?:, [^)]+)?\)\.)"
REFERENCE_ENTRY_PATTERN = (
    rf"(?:[{DASH_CLASS}]+\.\s+{REFERENCE_ENTRY_LABEL_PATTERN}"
    rf"|[A-ZÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+,\s+[^0-9]+?{REFERENCE_ENTRY_LABEL_PATTERN})"
)


def flow_reference_start(line: str) -> bool:
    return bool(re.match(rf"^{REFERENCE_ENTRY_PATTERN}", line))


def split_reference_segments(line: str) -> list[str]:
    return [
        segment.strip()
        for segment in re.split(
            rf"(?<=\.)\s+(?={REFERENCE_ENTRY_PATTERN})",
            line,
        )
        if segment.strip()
    ]


def flow_typical_line_length(lines: list[str], heading_map: dict[str, str]) -> float:
    lengths = [
        len(line.strip())
        for line in lines
        if len(line.strip()) >= 35 and not is_heading(line.strip(), heading_map)
    ]
    if not lengths:
        return 72.0
    return float(statistics.median(lengths))


def should_continue_heading(heading: str, line: str, typical_length: float) -> bool:
    stripped = line.strip()
    if not re.match(r"^[0-9]+\.", heading):
        return False
    if not stripped or re.match(r"^[0-9]+\.", stripped):
        return False
    if not (stripped[:1].islower() or re.search(r"\b(?:a|an|and|as|at|for|from|in|of|on|or|the|to|with)$", heading, flags=re.IGNORECASE)):
        return False
    if len(stripped) > max(48, int(typical_length * 0.7)):
        return False
    if re.search(r"[.!?;:]$", stripped):
        return False
    return True


def starts_new_flow_paragraph(previous: str, current: str, typical_length: float) -> bool:
    prev = previous.strip()
    curr = current.strip()
    if not prev or not curr:
        return False
    if not re.match(r'^[“"(\[]?[A-Z0-9]', curr):
        return False
    if not re.search(r'[.!?]["”\')\]]?$', prev):
        return False
    return len(prev) <= typical_length * 0.72


def blank_starts_new_paragraph(previous: str, current: str) -> bool:
    prev = previous.strip()
    curr = current.strip()
    if not prev or not curr:
        return True
    if not re.match(r'^[“"(\[]?[A-Z0-9]', curr):
        return False
    return bool(re.search(r'[.!?]["”\')\]]?$', prev))


def final_section_name(in_notes: bool, in_references: bool) -> str:
    if in_references:
        return "references"
    if in_notes:
        return "notes"
    return "body"


def looks_like_reference_paragraph(text: str) -> bool:
    segments = split_reference_segments(text)
    return bool(segments) and all(flow_reference_start(segment) for segment in segments)


def reorder_backmatter_columns(blocks: list[tuple[str, str]]) -> list[tuple[str, str]]:
    acknowledgments_index = next(
        (
            index
            for index, (block_type, content) in enumerate(blocks)
            if block_type == "heading" and content.casefold() in {"acknowledgments", "acknowledgements"}
        ),
        None,
    )
    if acknowledgments_index is None:
        return blocks

    bibliography_index = next(
        (
            index
            for index, (block_type, content) in enumerate(blocks[acknowledgments_index + 1 :], acknowledgments_index + 1)
            if block_type == "heading" and is_reference_section_name(content)
        ),
        None,
    )
    if bibliography_index is None:
        return blocks

    moved_start = acknowledgments_index
    while (
        moved_start > 0
        and blocks[moved_start - 1][0] == "paragraph"
        and looks_like_reference_paragraph(blocks[moved_start - 1][1])
    ):
        moved_start -= 1

    if moved_start == acknowledgments_index:
        return blocks

    moved_blocks = blocks[moved_start:acknowledgments_index]
    return blocks[:moved_start] + blocks[acknowledgments_index : bibliography_index + 1] + moved_blocks + blocks[bibliography_index + 1 :]


def normalize_reference_blocks(blocks: list[tuple[str, str]]) -> list[tuple[str, str]]:
    normalized: list[tuple[str, str]] = []
    in_references = False

    for block_type, content in blocks:
        if block_type == "heading":
            normalized.append((block_type, content))
            in_references = is_reference_section_name(content)
            continue

        if in_references:
            segments = split_reference_segments(content)
            if len(segments) > 1 and all(flow_reference_start(segment) for segment in segments):
                normalized.extend(("paragraph", segment) for segment in segments)
                continue

        normalized.append((block_type, content))

    return normalized


def strip_journal_boilerplate_blocks(blocks: list[tuple[str, str]]) -> list[tuple[str, str]]:
    if not any(block_type == "heading" and is_reference_section_name(content) for block_type, content in blocks):
        return blocks

    cleaned: list[tuple[str, str]] = []
    skipping = False

    for block_type, content in blocks:
        if block_type == "heading" and is_reference_section_name(content):
            skipping = False
            cleaned.append((block_type, content))
            continue

        if skipping:
            continue

        if block_type == "paragraph":
            marker_positions = [content.find(marker) for marker in BOILERPLATE_MARKERS if marker in content]
            if marker_positions:
                cut = min(position for position in marker_positions if position >= 0)
                prefix = content[:cut].rstrip()
                if prefix:
                    cleaned.append((block_type, prefix))
                skipping = True
                continue

        cleaned.append((block_type, content))

    return cleaned


def page_blocks_flow(
    raw_page: str,
    title: str,
    author: str,
    heading_map: dict[str, str],
    replacements: dict[str, str],
    is_first_page: bool,
    initial_section: str = "body",
    first_page_start_at: str | None = None,
    first_page_stop_before: str | None = None,
) -> tuple[list[tuple[str, str]], str]:
    lines = clean_page_lines(
        raw_page,
        title,
        author,
        is_first_page,
        mode="flow",
        first_page_start_at=first_page_start_at,
        first_page_stop_before=first_page_stop_before,
    )
    lines = repair_drop_caps(lines)
    blocks: list[tuple[str, str]] = []
    paragraph_parts: list[str] = []
    in_notes = initial_section == "notes"
    in_references = initial_section == "references"
    typical_length = flow_typical_line_length(lines, heading_map)

    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            next_nonblank = ""
            for candidate in lines[index + 1 :]:
                if candidate.strip():
                    next_nonblank = candidate.strip()
                    break
            if in_references:
                if paragraph_parts and (
                    not next_nonblank
                    or flow_reference_start(next_nonblank)
                ):
                    flush_paragraph(blocks, paragraph_parts, replacements)
                continue
            if in_notes:
                if paragraph_parts and (
                    not next_nonblank
                    or re.match(r"^\d+\.", next_nonblank)
                    or is_reference_heading(next_nonblank, heading_map)
                ):
                    flush_paragraph(blocks, paragraph_parts, replacements)
                continue
            if paragraph_parts and blank_starts_new_paragraph(paragraph_parts[-1], next_nonblank):
                flush_paragraph(blocks, paragraph_parts, replacements)
            continue

        if in_notes:
            if is_reference_heading(stripped, heading_map):
                flush_paragraph(blocks, paragraph_parts, replacements)
                blocks.append(("heading", normalize_heading_text(stripped, heading_map)))
                in_notes = False
                in_references = True
            elif re.match(r"^\d+\.", stripped):
                flush_paragraph(blocks, paragraph_parts, replacements)
                paragraph_parts.append(stripped)
            else:
                append_piece(paragraph_parts, stripped)
            continue

        if in_references:
            for segment in split_reference_segments(stripped):
                if flow_reference_start(segment):
                    flush_paragraph(blocks, paragraph_parts, replacements)
                    paragraph_parts.append(segment)
                else:
                    append_piece(paragraph_parts, segment)
            continue

        if is_heading(stripped, heading_map):
            flush_paragraph(blocks, paragraph_parts, replacements)
            heading_text = normalize_heading_text(stripped, heading_map)
            blocks.append(("heading", heading_text))
            if heading_text.lower() == "notes":
                in_notes = True
                in_references = False
            elif is_reference_section_name(heading_text):
                in_references = True
                in_notes = False
            else:
                in_notes = False
                in_references = False
            continue

        if (
            blocks
            and blocks[-1][0] == "heading"
            and not paragraph_parts
            and should_continue_heading(blocks[-1][1], stripped, typical_length)
        ):
            blocks[-1] = ("heading", f"{blocks[-1][1]} {stripped}")
            continue

        if not paragraph_parts:
            paragraph_parts.append(stripped)
            continue

        previous_piece = paragraph_parts[-1]
        if starts_new_flow_paragraph(previous_piece, stripped, typical_length):
            flush_paragraph(blocks, paragraph_parts, replacements)
            paragraph_parts.append(stripped)
            continue

        append_piece(paragraph_parts, stripped)

    flush_paragraph(blocks, paragraph_parts, replacements)
    blocks = reorder_backmatter_columns(blocks)
    blocks = normalize_reference_blocks(blocks)
    blocks = strip_journal_boilerplate_blocks(blocks)
    return blocks, final_section_name(in_notes, in_references)


def render_markdown(
    pagewise_blocks: list[tuple[int, list[tuple[str, str]]]],
    title: str,
    author: str,
    citation: str,
    doi: str,
    entry_url: str | None,
    pdf_url: str | None,
) -> str:
    lines = [
        f"# {title}",
        "",
        f"Author: {author}",
        f"Published in: {citation}",
    ]
    if doi:
        lines.append(f"DOI: [{doi}](https://doi.org/{doi})")
    if entry_url:
        lines.append(f"Canonical entry: {entry_url}")
    if pdf_url:
        lines.append(f"Published PDF: {pdf_url}")
    lines.extend(
        [
            "",
            "Machine-readable text companion generated from the PDF. Page markers follow the printed pagination.",
            "",
        ]
    )

    for page_number, blocks in pagewise_blocks:
        lines.append(f"[p. {page_number}]")
        lines.append("")
        for block_type, content in blocks:
            if block_type == "heading":
                heading_prefix = "###" if re.match(r"^\d+(?:\.\d+)+\s", content) else "##"
                lines.append(f"{heading_prefix} {content}")
            else:
                lines.append(content)
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_plain_text(
    pagewise_blocks: list[tuple[int, list[tuple[str, str]]]],
    title: str,
    author: str,
    citation: str,
    doi: str,
    entry_url: str | None,
    pdf_url: str | None,
) -> str:
    lines = [
        title,
        "",
        f"Author: {author}",
        f"Published in: {citation}",
    ]
    if doi:
        lines.append(f"DOI: {doi}")
    if entry_url:
        lines.append(f"Canonical entry: {entry_url}")
    if pdf_url:
        lines.append(f"Published PDF: {pdf_url}")
    lines.extend(
        [
            "",
            "Machine-readable text companion generated from the PDF. Page markers follow the printed pagination.",
            "",
        ]
    )

    for page_number, blocks in pagewise_blocks:
        lines.append(f"[p. {page_number}]")
        lines.append("")
        for block_type, content in blocks:
            lines.append(content if block_type == "paragraph" else content.upper())
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Markdown and plain-text companions from a PDF.")
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("output_stem", type=Path, help="Path without extension for the generated files.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--citation", required=True)
    parser.add_argument("--doi", required=True)
    parser.add_argument("--start-page", required=True, type=int)
    parser.add_argument("--entry-url")
    parser.add_argument("--pdf-url")
    parser.add_argument("--pdftotext-mode", choices=["layout", "flow"], default="layout")
    parser.add_argument("--first-page-start-at")
    parser.add_argument("--first-page-stop-before")
    parser.add_argument("--heading-map", action="append", default=[])
    parser.add_argument("--replace", action="append", default=[])
    args = parser.parse_args()

    heading_map = parse_mapping(args.heading_map)
    replacements = parse_mapping(args.replace)

    page_count = pdf_page_count(args.pdf_path)
    pagewise_blocks: list[tuple[int, list[tuple[str, str]]]] = []
    current_section = "body"

    for physical_page in range(1, page_count + 1):
        raw_page = extract_page(args.pdf_path, physical_page, args.pdftotext_mode)
        if args.pdftotext_mode == "flow":
            blocks, current_section = page_blocks_flow(
                raw_page=raw_page,
                title=args.title,
                author=args.author,
                heading_map=heading_map,
                replacements=replacements,
                is_first_page=physical_page == 1,
                initial_section=current_section,
                first_page_start_at=args.first_page_start_at,
                first_page_stop_before=args.first_page_stop_before,
            )
        else:
            blocks, current_section = page_blocks_layout(
                raw_page=raw_page,
                title=args.title,
                author=args.author,
                heading_map=heading_map,
                replacements=replacements,
                is_first_page=physical_page == 1,
                initial_section=current_section,
                first_page_start_at=args.first_page_start_at,
                first_page_stop_before=args.first_page_stop_before,
            )
        if blocks:
            pagewise_blocks.append((args.start_page + physical_page - 1, blocks))

    args.output_stem.parent.mkdir(parents=True, exist_ok=True)
    markdown_output = render_markdown(
        pagewise_blocks=pagewise_blocks,
        title=args.title,
        author=args.author,
        citation=args.citation,
        doi=args.doi,
        entry_url=args.entry_url,
        pdf_url=args.pdf_url,
    )
    plain_text_output = render_plain_text(
        pagewise_blocks=pagewise_blocks,
        title=args.title,
        author=args.author,
        citation=args.citation,
        doi=args.doi,
        entry_url=args.entry_url,
        pdf_url=args.pdf_url,
    )

    args.output_stem.with_suffix(".md").write_text(markdown_output, encoding="utf-8")
    args.output_stem.with_suffix(".txt").write_text(plain_text_output, encoding="utf-8")


if __name__ == "__main__":
    main()
