from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class TagTranslation:
    term: str
    label: str


_ROMAN_NUMERALS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
    7: "VII",
    8: "VIII",
    9: "IX",
    10: "X",
    11: "XI",
    12: "XII",
    13: "XIII",
    14: "XIV",
    15: "XV",
    16: "XVI",
    17: "XVII",
    18: "XVIII",
    19: "XIX",
    20: "XX",
    21: "XXI",
}


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = (
        text.replace("ß", "ss")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
    )
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


_APOSTROPHES = {"'", "’", "ʼ", "‛", "`", "´"}
_DASHES = {"-", "‐", "‑", "‒", "–", "—", "―"}


def taxonomy_slug(text: str) -> str:
    """
    Generate a URL path segment for Hugo taxonomy terms.

    Key differences vs `_slugify()`:
    - preserves accents/umlauts as written in the term
    - removes apostrophes instead of turning them into separators
    """
    text = unicodedata.normalize("NFC", text.strip().lower())
    if not text:
        return ""

    # Hugo-style behavior observed in this site output: drop apostrophes (l'esprit -> lesprit).
    text = "".join(ch for ch in text if ch not in _APOSTROPHES)

    out: list[str] = []
    prev_sep = False
    for ch in text:
        cat = unicodedata.category(ch)
        if cat[0] in ("L", "M", "N"):
            out.append(ch)
            prev_sep = False
            continue

        if ch in _DASHES or cat.startswith("Z"):
            if not prev_sep:
                out.append("-")
                prev_sep = True
            continue

        # Treat remaining punctuation/symbols as separators.
        if not prev_sep:
            out.append("-")
            prev_sep = True

    slug = "".join(out)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def _titlecase_words(text: str) -> str:
    return " ".join(w[:1].upper() + w[1:] if w else w for w in text.split(" "))


_FR_SLUG_OVERRIDES: dict[str, TagTranslation] = {
    "history-of-philosophy": TagTranslation("histoire-de-la-philosophie", "histoire de la philosophie"),
    "theoretical-philosophy": TagTranslation("philosophie-théorique", "philosophie théorique"),
    "practical-philosophy": TagTranslation("philosophie-pratique", "philosophie pratique"),
    "philosophy-of-mind": TagTranslation("philosophie-de-l'esprit", "philosophie de l’esprit"),
    "philosophy-of-language": TagTranslation("philosophie-du-langage", "philosophie du langage"),
    "philosophy-of-law": TagTranslation("philosophie-du-droit", "philosophie du droit"),
    "philosophy-of-history": TagTranslation("philosophie-de-l'histoire", "philosophie de l’histoire"),
    "philosophy-of-action": TagTranslation("philosophie-de-l'action", "philosophie de l’action"),
    "philosophy-of-ai": TagTranslation("philosophie-de-l-ia", "philosophie de l’IA"),
    "explainable-ai": TagTranslation("ia-explicable", "IA explicable"),
    "philosophy-of-technology": TagTranslation("philosophie-de-la-technologie", "philosophie de la technologie"),
    "social-epistemology": TagTranslation("épistémologie-sociale", "épistémologie sociale"),
    "moral-luck": TagTranslation("chance-morale", "chance morale"),
    "value-conflict": TagTranslation("conflit-de-valeurs", "conflit de valeurs"),
    "virtue-ethics": TagTranslation("éthique-des-vertus", "éthique des vertus"),
    "virtue-theory": TagTranslation("théorie-des-vertus", "théorie des vertus"),
    "knowledge-first-epistemology": TagTranslation("épistémologie-du-primat-de-la-connaissance", "épistémologie du primat de la connaissance"),
    "wwii": TagTranslation("seconde-guerre-mondiale", "Seconde Guerre mondiale"),
    "internal-reasons": TagTranslation("internal-raisons", "raisons internes"),
}


_DE_SLUG_OVERRIDES: dict[str, TagTranslation] = {
    "history-of-philosophy": TagTranslation("geschichte-der-philosophie", "Geschichte der Philosophie"),
    "theoretical-philosophy": TagTranslation("theoretische-philosophie", "Theoretische Philosophie"),
    "practical-philosophy": TagTranslation("praktische-philosophie", "Praktische Philosophie"),
    "philosophy-of-mind": TagTranslation("philosophie-des-geistes", "Philosophie des Geistes"),
    "philosophy-of-language": TagTranslation("sprachphilosophie", "Sprachphilosophie"),
    "philosophy-of-law": TagTranslation("rechtsphilosophie", "Rechtsphilosophie"),
    "philosophy-of-history": TagTranslation("geschichtsphilosophie", "Geschichtsphilosophie"),
    "philosophy-of-action": TagTranslation("handlungsphilosophie", "Handlungsphilosophie"),
    "philosophy-of-ai": TagTranslation("philosophie-der-ki", "Philosophie der KI"),
    "philosophy-of-technology": TagTranslation("technikphilosophie", "Technikphilosophie"),
    "social-epistemology": TagTranslation("soziale-erkenntnistheorie", "Soziale Erkenntnistheorie"),
    "moral-luck": TagTranslation("moralisches-glück", "Moralisches Glück"),
    "value-conflict": TagTranslation("wertkonflikt", "Wertkonflikt"),
    "virtue-ethics": TagTranslation("tugendethik", "Tugendethik"),
    "virtue-theory": TagTranslation("tugendtheorie", "Tugendtheorie"),
    "knowledge-first-epistemology": TagTranslation("knowledge-first-erkenntnistheorie", "Knowledge-first Erkenntnistheorie"),
    "explainable-ai": TagTranslation("erklaerbare-ki", "erklärbare KI"),
    "internalism": TagTranslation("internalismus", "Internalismus"),
    "common-heritage": TagTranslation("gemeinsames-erbe", "gemeinsames Erbe"),
    "genealogical-method": TagTranslation("genealogische-methode", "genealogische Methode"),
    "methodological-pragmatism": TagTranslation("methodologischer-pragmatismus", "methodologischer Pragmatismus"),
    "wwii": TagTranslation("zweiter-weltkrieg", "Zweiter Weltkrieg"),
    "internal-reasons": TagTranslation("interne-gruende", "interne Gründe"),
}


_FR_TOKEN_MAP = {
    "accountability": "responsabilité",
    "action": "action",
    "adaptation": "adaptation",
    "affirmative": "affirmatif",
    "agency": "agentivite",
    "ai": "ia",
    "algorithmic": "algorithmique",
    "amelioration": "amelioration",
    "analysis": "analyse",
    "analytic": "analytique",
    "ancient": "ancienne",
    "anti": "anti",
    "architecture": "architecture",
    "aristotle": "aristote",
    "asceticism": "ascetisme",
    "aspirational": "aspirationnel",
    "asystematicity": "asystematicite",
    "authority": "autorite",
    "autonomy": "autonomie",
    "basel": "bale",
    "bioethics": "bioethique",
    "biotechnology": "biotechnologie",
    "blame": "blâme",
    "book": "livre",
    "british": "britannique",
    "canon": "canon",
    "causal": "causal",
    "causalism": "causalisme",
    "causation": "causalite",
    "chain": "chaine",
    "choice": "choix",
    "cognition": "cognition",
    "cognitive": "cognitif",
    "coherence": "cohérence",
    "common": "commun",
    "commons": "communs",
    "competence": "compétence",
    "compression": "compression",
    "concept": "concept",
    "concepts": "concepts",
    "conceptual": "conceptuel",
    "conflict": "conflit",
    "connectionism": "connexionnisme",
    "consequentialism": "consequentialisme",
    "contestability": "contestabilite",
    "context": "contexte",
    "contextual": "contextuel",
    "continuity": "continuite",
    "coordination": "coordination",
    "critical": "critique",
    "critique": "critique",
    "cultural": "culturel",
    "culture": "culture",
    "decision": "decision",
    "deontology": "deontologie",
    "dependency": "dependance",
    "democracy": "democratie",
    "deliberation": "délibération",
    "dirty": "sale",
    "discursive": "discursif",
    "dna": "adn",
    "duties": "devoirs",
    "early": "moderne",
    "equality": "egalite",
    "epistemic": "epistemique",
    "epistemology": "epistemologie",
    "ethics": "ethique",
    "ethical": "ethique",
    "ethnographic": "ethnographique",
    "evaluation": "évaluation",
    "evidence": "preuve",
    "exchange": "echange",
    "existentialism": "existentialisme",
    "experience": "expérience",
    "explainability": "explicabilite",
    "explanation": "explication",
    "explication": "explicitation",
    "feature": "caractéristique",
    "geometry": "géométrie",
    "formation": "formation",
    "expressivism": "expressivisme",
    "fairness": "equite",
    "fault": "faute",
    "fictionalism": "fictionnalisme",
    "forgiveness": "pardon",
    "freedom": "liberte",
    "function": "fonction",
    "functional": "fonctionnel",
    "functionalism": "fonctionnalisme",
    "functions": "fonctions",
    "genealogy": "genealogie",
    "genealogical": "genealogique",
    "genealogies": "généalogies",
    "genetics": "genetique",
    "genome": "genome",
    "governance": "gouvernance",
    "handbuch": "handbuch",
    "hands": "mains",
    "hermeneutics": "hermeneutique",
    "historicism": "historicisme",
    "historicist": "historiciste",
    "historiography": "historiographie",
    "history": "histoire",
    "hobbes": "hobbes",
    "humanistic": "humaniste",
    "ideology": "ideologie",
    "implementation": "implementation",
    "institutional": "institutionnel",
    "intellectual": "intellectuel",
    "interpretability": "interpretabilite",
    "interpretation": "interpretation",
    "fiduciary": "fiduciaire",
    "duty": "devoir",
    "jurisprudence": "jurisprudence",
    "justice": "justice",
    "justification": "justification",
    "kantian": "kantien",
    "kantianism": "kantisme",
    "knowledge": "connaissance",
    "law": "droit",
    "legal": "juridique",
    "legitimacy": "legitimite",
    "liberalism": "liberalisme",
    "liberty": "liberte",
    "llm": "llm",
    "love": "amour",
    "luck": "chance",
    "machine": "machine",
    "meaning": "sens",
    "meta": "meta",
    "metaphilosophy": "metaphilosophie",
    "metaphysics": "metaphysique",
    "method": "methode",
    "methodology": "methodologie",
    "mind": "esprit",
    "model": "modele",
    "modeling": "modelisation",
    "moral": "moral",
    "morality": "moralite",
    "motivation": "motivation",
    "naturalism": "naturalisme",
    "needs": "besoins",
    "neo": "neo",
    "nietzsche": "nietzsche",
    "normative": "normatif",
    "normativity": "normativite",
    "obedience": "obeissance",
    "obligation": "obligation",
    "patents": "brevets",
    "phenomenology": "phenomenologie",
    "philosophy": "philosophie",
    "pluralism": "pluralisme",
    "political": "politique",
    "politics": "politique",
    "power": "pouvoir",
    "practical": "pratique",
    "pragmatic": "pragmatique",
    "pragmatics": "pragmatique",
    "pragmatism": "pragmatisme",
    "privacy": "vie-privee",
    "property": "propriete",
    "psychology": "psychologie",
    "public": "public",
    "rationality": "rationalite",
    "realism": "realisme",
    "reason": "raison",
    "reasoning": "raisonnement",
    "reasons": "raisons",
    "representation": "representation",
    "responsibility": "responsabilite",
    "rights": "droits",
    "romanticism": "romantisme",
    "rule": "regle",
    "scalability": "mise-a-lechelle",
    "science": "science",
    "self": "soi",
    "sense": "sens",
    "social": "social",
    "sovereignty": "souverainete",
    "state": "etat",
    "stoicism": "stoicisme",
    "strength": "force",
    "technology": "technologie",
    "theoretical": "theorique",
    "theory": "theorie",
    "truth": "verite",
    "truthfulness": "veracite",
    "trust": "confiance",
    "understanding": "comprehension",
    "value": "valeur",
    "values": "valeurs",
    "virtue": "vertu",
    "voluntary": "volontaire",
    "voluntariness": "volontarite",
    "war": "guerre",
    "williams": "williams",
    "wittgenstein": "wittgenstein",
}


_DE_TOKEN_MAP = {
    "accountability": "rechenschaftspflicht",
    "action": "handlung",
    "adaptation": "anpassung",
    "affirmative": "affirmativ",
    "agency": "handlungsfaehigkeit",
    "ai": "ki",
    "algorithmic": "algorithmisch",
    "amelioration": "verbesserung",
    "analysis": "analyse",
    "analytic": "analytisch",
    "ancient": "antike",
    "anti": "anti",
    "architecture": "architektur",
    "aristotle": "aristoteles",
    "asceticism": "asketismus",
    "aspirational": "aspirational",
    "asystematicity": "asystematizitaet",
    "authority": "autoritaet",
    "autonomy": "autonomie",
    "basel": "basel",
    "bioethics": "bioethik",
    "biotechnology": "biotechnologie",
    "blame": "tadel",
    "book": "buch",
    "british": "britisch",
    "canon": "kanon",
    "causal": "kausal",
    "causalism": "kausalismus",
    "causation": "kausalitaet",
    "chain": "kette",
    "cognition": "kognition",
    "cognitive": "kognitiv",
    "coherence": "kohärenz",
    "common": "gemeinsam",
    "commons": "allmende",
    "competence": "kompetenz",
    "compression": "kompression",
    "concept": "begriff",
    "concepts": "begriffe",
    "conceptual": "begrifflich",
    "conflict": "konflikt",
    "connectionism": "konnektionismus",
    "consequentialism": "konsequentialismus",
    "contestability": "bestreitbarkeit",
    "context": "kontext",
    "continuity": "kontinuitaet",
    "coordination": "koordination",
    "critical": "kritisch",
    "critique": "kritik",
    "cultural": "kulturell",
    "culture": "kultur",
    "decision": "entscheidung",
    "deontology": "deontologie",
    "dependency": "abhaengigkeit",
    "democracy": "demokratie",
    "deliberation": "deliberation",
    "discursive": "diskursiv",
    "dna": "dns",
    "duties": "pflichten",
    "early": "frueh",
    "equality": "gleichheit",
    "epistemic": "epistemisch",
    "epistemology": "erkenntnistheorie",
    "ethics": "ethik",
    "ethical": "ethisch",
    "ethnographic": "ethnographisch",
    "evaluation": "bewertung",
    "evidence": "evidenz",
    "exchange": "austausch",
    "existentialism": "existentialismus",
    "experience": "erfahrung",
    "explainability": "erklaerbarkeit",
    "explanation": "erklaerung",
    "explication": "explizierung",
    "expressivism": "expressivismus",
    "fairness": "fairness",
    "fault": "schuld",
    "fictionalism": "fiktionalismus",
    "forgiveness": "vergebung",
    "freedom": "freiheit",
    "function": "funktion",
    "functional": "funktional",
    "functionalism": "funktionalismus",
    "functions": "funktionen",
    "genealogy": "genealogie",
    "genealogical": "genealogisch",
    "genealogies": "genealogien",
    "genetics": "genetik",
    "genome": "genom",
    "governance": "governance",
    "handbuch": "handbuch",
    "hermeneutics": "hermeneutik",
    "historicism": "historismus",
    "historicist": "historistisch",
    "historiography": "historiographie",
    "history": "geschichte",
    "hobbes": "hobbes",
    "humanistic": "humanistisch",
    "ideology": "ideologie",
    "implementation": "implementierung",
    "institutional": "institutionell",
    "intellectual": "intellektuell",
    "interpretability": "interpretierbarkeit",
    "interpretation": "interpretation",
    "internalism": "internalismus",
    "jurisprudence": "rechtslehre",
    "justice": "gerechtigkeit",
    "justification": "rechtfertigung",
    "kantian": "kantisch",
    "kantianism": "kantianismus",
    "knowledge": "wissen",
    "law": "recht",
    "legal": "rechtlich",
    "legitimacy": "legitimitaet",
    "liberalism": "liberalismus",
    "liberty": "freiheit",
    "llm": "llm",
    "love": "liebe",
    "luck": "glueck",
    "machine": "maschine",
    "meaning": "bedeutung",
    "meta": "meta",
    "metaphilosophy": "metaphilosophie",
    "metaphysics": "metaphysik",
    "method": "methode",
    "methodology": "methodologie",
    "mind": "geist",
    "model": "modell",
    "modeling": "modellierung",
    "moral": "moralisch",
    "morality": "moral",
    "motivation": "motivation",
    "naturalism": "naturalismus",
    "needs": "beduerfnisse",
    "nietzsche": "nietzsche",
    "normative": "normativ",
    "normativity": "normativitaet",
    "obedience": "gehorsam",
    "obligation": "verpflichtung",
    "patents": "patente",
    "phenomenology": "phaenomenologie",
    "philosophy": "philosophie",
    "pluralism": "pluralismus",
    "political": "politisch",
    "politics": "politik",
    "power": "macht",
    "practical": "praktisch",
    "pragmatic": "pragmatisch",
    "pragmatics": "pragmatik",
    "pragmatism": "pragmatismus",
    "privacy": "privatsphaere",
    "property": "eigentum",
    "psychology": "psychologie",
    "public": "oeffentlich",
    "rationality": "rationalitaet",
    "realism": "realismus",
    "reason": "grund",
    "reasoning": "schlussfolgern",
    "reasons": "gruende",
    "representation": "repraesentation",
    "responsibility": "verantwortung",
    "rights": "rechte",
    "romanticism": "romantik",
    "rule": "regel",
    "scalability": "skalierbarkeit",
    "science": "wissenschaft",
    "self": "selbst",
    "sense": "sinn",
    "social": "sozial",
    "sovereignty": "souveraenitaet",
    "state": "staat",
    "stoicism": "stoizismus",
    "strength": "staerke",
    "technology": "technologie",
    "theoretical": "theoretisch",
    "theory": "theorie",
    "truth": "wahrheit",
    "truthfulness": "wahrhaftigkeit",
    "trust": "vertrauen",
    "understanding": "verstaendnis",
    "value": "wert",
    "values": "werte",
    "virtue": "tugend",
    "voluntary": "freiwillig",
    "voluntariness": "freiwilligkeit",
    "war": "krieg",
    "williams": "williams",
    "wittgenstein": "wittgenstein",
}


_CENTURY_RE = re.compile(r"^(\d+)(st|nd|rd|th)-century$")


def translate_tag(en_slug: str, lang: str) -> TagTranslation:
    if lang == "fr" and en_slug in _FR_SLUG_OVERRIDES:
        return _FR_SLUG_OVERRIDES[en_slug]
    if lang == "de" and en_slug in _DE_SLUG_OVERRIDES:
        return _DE_SLUG_OVERRIDES[en_slug]

    m = _CENTURY_RE.match(en_slug)
    if m:
        century = int(m.group(1))
        if lang == "fr":
            roman = _ROMAN_NUMERALS.get(century, str(century))
            return TagTranslation(f"{century}e-siècle", f"{roman}e siècle")
        if lang == "de":
            return TagTranslation(f"{century}-jahrhundert", f"{century}. Jahrhundert")

    tokens = en_slug.split("-")
    if lang == "fr":
        translated_tokens = [_FR_TOKEN_MAP.get(t, t) for t in tokens]
        term = "-".join(translated_tokens)
        label = " ".join(translated_tokens)
        return TagTranslation(term, label)
    if lang == "de":
        translated_tokens = [_DE_TOKEN_MAP.get(t, t) for t in tokens]
        term = "-".join(translated_tokens)
        label = _titlecase_words(" ".join(translated_tokens))
        return TagTranslation(term, label)

    raise ValueError(f"Unsupported lang: {lang}")
