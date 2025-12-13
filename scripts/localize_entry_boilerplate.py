from __future__ import annotations

import glob
import re


def rewrite(text: str, lang: str) -> str:
    # Translate some recurring boilerplate while trying not to touch journal/book titles.
    if lang == "fr":
        text = re.sub(r"^With (.+?)\.\s*$", r"Avec \1.", text, flags=re.M)
        text = re.sub(r"\bWith ([A-Z][^.\n]+)\.", r"Avec \1.", text)
        text = text.replace("By invitation.", "Sur invitation.")
        text = text.replace("Invited commentary.", "Commentaire invité.")
        text = text.replace("Invited Commentary.", "Commentaire invité.")
        text = text.replace("Symposium on my ", "Symposium sur mon ")
        text = text.replace("Symposium on ", "Symposium sur ")
        text = re.sub(r"^In \*", "Dans *", text, flags=re.M)
    elif lang == "de":
        text = re.sub(r"^With (.+?)\.\s*$", r"Mit \1.", text, flags=re.M)
        text = re.sub(r"\bWith ([A-Z][^.\n]+)\.", r"Mit \1.", text)
        text = text.replace("By invitation.", "Auf Einladung.")
        text = text.replace("Invited commentary.", "Eingeladener Kommentar.")
        text = text.replace("Invited Commentary.", "Eingeladener Kommentar.")
        text = text.replace("Symposium on my ", "Symposium zu meinem ")
        text = text.replace("Symposium on ", "Symposium zu ")
    else:
        raise ValueError(lang)
    return text


def main() -> None:
    for lang in ("fr", "de"):
        for path in glob.glob(f"content/entries/*.{lang}.md"):
            src = open(path, "r", encoding="utf-8").read()
            out = rewrite(src, lang)
            if out != src:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out)


if __name__ == "__main__":
    main()

