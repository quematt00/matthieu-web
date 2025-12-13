from __future__ import annotations

import glob
import re
from collections import Counter

from i18n_tags import translate_tag


def parse_list_block(frontmatter: str, key: str) -> list[str]:
    m = re.search(rf"^{re.escape(key)}:\n((?:\s+- .*?\n)+)", frontmatter, re.M)
    if not m:
        return []
    out: list[str] = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        val = line[2:].strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        out.append(val)
    return out


def main() -> None:
    tag_slugs: set[str] = set()
    for path in glob.glob("content/entries/*.md"):
        txt = open(path, "r", encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
        if not m:
            continue
        fm = m.group(1)
        for t in parse_list_block(fm, "tags"):
            tag_slugs.add(t)

    stats: dict[str, Counter[str]] = {"fr": Counter(), "de": Counter()}
    for lang in ("fr", "de"):
        for t in tag_slugs:
            tr = translate_tag(t, lang).term
            stats[lang]["total"] += 1
            stats[lang]["changed" if tr != t else "unchanged"] += 1

    for lang in ("fr", "de"):
        print(lang, dict(stats[lang]))

    # Show some unchanged tags for review.
    for lang in ("fr", "de"):
        unchanged = sorted(t for t in tag_slugs if translate_tag(t, lang).term == t)
        print(f"\n{lang} unchanged sample ({min(50, len(unchanged))} of {len(unchanged)}):")
        for t in unchanged[:50]:
            print(" ", t)


if __name__ == "__main__":
    main()
