#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIRS = (
    REPO_ROOT / "content" / "entries",
    REPO_ROOT / "content" / "books",
)
COMPANION_DIR = REPO_ROOT / "static" / "llm" / "papers"
SKIP_ENTRY_SUFFIXES = (".de.md", ".fr.md")
BODY_START_PATTERN = re.compile(r"^\[p\. \d+\]$", flags=re.MULTILINE)
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n(.*)$", flags=re.DOTALL)
LLM_MD_PATTERN = re.compile(r'^llm_text_markdown:\s*"([^"]+)"\s*$', flags=re.MULTILINE)
LLM_TXT_PATTERN = re.compile(r'^llm_text_plain:\s*"([^"]+)"\s*$', flags=re.MULTILINE)
TITLE_PATTERN = re.compile(r'^title:\s*"(.+)"\s*$', flags=re.MULTILINE)


ARTIFACT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("download boilerplate", re.compile(r"Downloaded from ")),
    ("web page header", re.compile(r"\|\s+Aeon (?:Essay|Essays)\b")),
    ("page counter", re.compile(r"\bPage \d+ of \d+\b")),
    ("separator artifact", re.compile(r"\*\*\*")),
    ("journal boilerplate", re.compile(r"\bwileyonlinelibrary\.com\b", flags=re.IGNORECASE)),
    ("contact boilerplate", re.compile(r"\b(?:Correspondence|Email:|ORCID)\b")),
    ("web footer", re.compile(r"\baeon\.co(?:\s+\d{1,2}\s+\w+\s+\d{4})?\b", flags=re.IGNORECASE)),
)


@dataclass
class ArtifactHit:
    file: str
    line: int
    issue: str
    snippet: str


@dataclass
class AuditResult:
    total_english_works: int
    works_with_companions: int
    missing_companions: list[str]
    broken_metadata_paths: list[str]
    orphan_companions: list[str]
    artifact_hits: list[ArtifactHit]


def split_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        raise ValueError("Expected YAML frontmatter delimited by ---")
    return match.group(1), match.group(2)


def extract_title(frontmatter: str, fallback: str) -> str:
    match = TITLE_PATTERN.search(frontmatter)
    return match.group(1) if match else fallback


def english_work_paths() -> list[Path]:
    works: list[Path] = []
    for content_dir in CONTENT_DIRS:
        for path in sorted(content_dir.glob("*.md")):
            if path.name.endswith(SKIP_ENTRY_SUFFIXES):
                continue
            works.append(path)
    return works


def extract_companion_paths(frontmatter: str) -> tuple[str | None, str | None]:
    md_match = LLM_MD_PATTERN.search(frontmatter)
    txt_match = LLM_TXT_PATTERN.search(frontmatter)
    md_path = md_match.group(1) if md_match else None
    txt_path = txt_match.group(1) if txt_match else None
    return md_path, txt_path


def resolve_static_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    return REPO_ROOT / "static" / path_value.lstrip("/")


def companion_body(text: str) -> str:
    match = BODY_START_PATTERN.search(text)
    if not match:
        return text
    return text[match.start() :]


def is_numeric_artifact_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("[p. "):
        return False
    if stripped in {"]", ".)"}:
        return True
    if any(0xF000 <= ord(char) <= 0xF8FF for char in stripped if not char.isspace()):
        return True
    if re.fullmatch(r"\d+\.", stripped):
        return False
    if re.fullmatch(r"\d+", stripped):
        return len(stripped) >= 3
    if any(char.isalpha() for char in stripped):
        return False
    numeric_like = 0
    for char in stripped:
        if char.isspace():
            continue
        if char.isdigit() or char in {"(", ")", "[", "]", ".", ",", ":", ";", "-", "–", "—"}:
            numeric_like += 1
            continue
        category = ord(char)
        if 0xF000 <= category <= 0xF8FF:
            numeric_like += 1
            continue
        try:
            if char.isnumeric():
                numeric_like += 1
                continue
        except Exception:
            pass
        return False
    return numeric_like > 0


def scan_artifacts(companion_path: Path) -> list[ArtifactHit]:
    hits: list[ArtifactHit] = []
    text = companion_body(companion_path.read_text(encoding="utf-8"))
    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in ARTIFACT_PATTERNS:
            if label == "contact boilerplate" and line_number > 120:
                continue
            if pattern.search(line):
                hits.append(
                    ArtifactHit(
                        file=str(companion_path.relative_to(REPO_ROOT)),
                        line=line_number,
                        issue=label,
                        snippet=line.strip(),
                    )
                )
        if is_numeric_artifact_line(line):
            hits.append(
                ArtifactHit(
                    file=str(companion_path.relative_to(REPO_ROOT)),
                    line=line_number,
                    issue="isolated page-number artifact",
                    snippet=line.strip(),
                )
            )
    return hits


def audit() -> AuditResult:
    works = english_work_paths()
    missing_companions: list[str] = []
    broken_metadata_paths: list[str] = []
    artifact_hits: list[ArtifactHit] = []
    referenced_companions: set[Path] = set()
    works_with_companions = 0

    for work_path in works:
        text = work_path.read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(text)
        title = extract_title(frontmatter, work_path.stem)
        md_value, txt_value = extract_companion_paths(frontmatter)
        md_path = resolve_static_path(md_value)
        txt_path = resolve_static_path(txt_value)
        relative_work = str(work_path.relative_to(REPO_ROOT))

        if not md_value and not txt_value:
            missing_companions.append(relative_work)
            continue

        if not md_value or not txt_value:
            broken_metadata_paths.append(
                f"{relative_work}: incomplete metadata (expected both markdown and plain-text companion paths)"
            )
            continue

        missing_files: list[str] = []
        assert md_path is not None
        assert txt_path is not None
        if not md_path.exists():
            missing_files.append(md_value)
        if not txt_path.exists():
            missing_files.append(txt_value)

        if missing_files:
            broken_metadata_paths.append(
                f"{relative_work}: missing companion file(s): {', '.join(missing_files)}"
            )
            continue

        works_with_companions += 1
        referenced_companions.add(md_path.resolve())
        referenced_companions.add(txt_path.resolve())
        artifact_hits.extend(scan_artifacts(md_path))

        if not title:
            broken_metadata_paths.append(f"{relative_work}: could not determine title")

    orphan_companions: list[str] = []
    for companion_path in sorted(COMPANION_DIR.glob("*")):
        if companion_path.name in {"index.md", "index.json", "index.html", "sitemap.xml"}:
            continue
        if companion_path.suffix not in {".md", ".txt"}:
            continue
        if companion_path.resolve() not in referenced_companions:
            orphan_companions.append(str(companion_path.relative_to(REPO_ROOT)))

    return AuditResult(
        total_english_works=len(works),
        works_with_companions=works_with_companions,
        missing_companions=missing_companions,
        broken_metadata_paths=broken_metadata_paths,
        orphan_companions=orphan_companions,
        artifact_hits=artifact_hits,
    )


def print_text_report(result: AuditResult, artifact_limit: int) -> None:
    print("Coverage")
    print(f"- English works: {result.total_english_works}")
    print(f"- With companions: {result.works_with_companions}")
    print(f"- Missing companions: {len(result.missing_companions)}")
    if result.missing_companions:
        for item in result.missing_companions:
            print(f"  - {item}")

    print("\nBroken Metadata Paths")
    if result.broken_metadata_paths:
        for item in result.broken_metadata_paths:
            print(f"- {item}")
    else:
        print("- None")

    print("\nOrphan Companions")
    if result.orphan_companions:
        for item in result.orphan_companions:
            print(f"- {item}")
    else:
        print("- None")

    print("\nArtifact Hits")
    print(f"- Total hits: {len(result.artifact_hits)}")
    for hit in result.artifact_hits[:artifact_limit]:
        print(f"- {hit.file}:{hit.line} [{hit.issue}] {hit.snippet}")
    remaining = len(result.artifact_hits) - min(len(result.artifact_hits), artifact_limit)
    if remaining > 0:
        print(f"- ... and {remaining} more")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the LLM full-text companion layer.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a text report.")
    parser.add_argument(
        "--artifact-limit",
        type=int,
        default=40,
        help="Maximum number of artifact hits to print in text mode.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any missing companions, broken paths, orphan companions, or artifact hits are found.",
    )
    args = parser.parse_args()

    result = audit()

    if args.json:
        payload = asdict(result)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_text_report(result, args.artifact_limit)

    if args.strict and (
        result.missing_companions
        or result.broken_metadata_paths
        or result.orphan_companions
        or result.artifact_hits
    ):
        sys.exit(1)


if __name__ == "__main__":
    main()
