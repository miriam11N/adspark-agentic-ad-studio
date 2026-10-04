import re

from schemas import AdBrief


def _clean_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def _first_meaningful_word(text: str, fallback: str) -> str:
    stop_words = {
        "and",
        "the",
        "for",
        "with",
        "your",
        "from",
        "that",
        "this",
        "into",
        "more",
        "zero",
        "added",
        "real",
    }

    for word in _clean_words(text):
        if len(word) >= 4 and word not in stop_words:
            return word.title()

    return fallback


def _fit_to_word_range(
    tagline: str,
    brief: AdBrief,
    fillers: list[str],
) -> str:
    """
    Make deterministic mock candidates fit the exact user-selected range.
    Later, the LLM replaces this helper naturally.
    """

    min_words, max_words = brief.tagline_word_range
    words = tagline.split()

    filler_index = 0

    while len(words) < min_words:
        words.append(fillers[filler_index % len(fillers)])
        filler_index += 1

    return " ".join(words[:max_words])


def generate_mock_taglines(brief: AdBrief, n: int = 5) -> list[str]:
    """
    Brief-aware temporary Copywriter.

    It does not try to be a real copywriting model. Its job is to:
    - use product, USP, and requested words,
    - respect the selected tagline length,
    - produce deterministic candidates for workflow testing.
    """

    product_word = _first_meaningful_word(
        brief.product_name,
        fallback="Your Brand",
    )
    benefit_word = _first_meaningful_word(
        brief.usp,
        fallback="Value",
    )

    requested_word = (
        _first_meaningful_word(
            brief.include_words[0],
            fallback=benefit_word,
        )
        if brief.include_words
        else benefit_word
    )

    fillers = [
        "With",
        "Confidence",
        "Today",
        "Everywhere",
        "Made",
        "Simple",
        "For",
        "You",
        "Now",
    ]

    templates = [
        f"{requested_word} Made Simple",
        f"{benefit_word} With Confidence",
        f"{product_word} Built For More",
        f"Smarter {benefit_word} Starts Here",
        f"Choose {requested_word} Every Day",
        f"{product_word} Makes Work Simple",
        f"Move Forward With {benefit_word}",
    ]

    candidates = []
    seen = set()

    for template in templates:
        tagline = _fit_to_word_range(template, brief, fillers)
        normalized = tagline.lower().strip()

        if normalized not in seen:
            seen.add(normalized)
            candidates.append(tagline)

        if len(candidates) == n:
            break

    return candidates


def generate_mock_rewrite_taglines(
    brief: AdBrief,
    rewrite_instruction: str,
    n: int = 5,
) -> list[str]:
    """
    Brief-aware temporary rewrite generator.

    In the final version, this becomes an LLM call:
    structured brief + rejected candidates + critic feedback -> new candidates.
    """

    product_word = _first_meaningful_word(
        brief.product_name,
        fallback="Your Brand",
    )
    benefit_word = _first_meaningful_word(
        brief.usp,
        fallback="Value",
    )

    requested_word = (
        _first_meaningful_word(
            brief.include_words[0],
            fallback=benefit_word,
        )
        if brief.include_words
        else benefit_word
    )

    fillers = [
        "For",
        "Every",
        "Team",
        "With",
        "Confidence",
        "At",
        "Scale",
        "Today",
        "Now",
    ]

    templates = [
        f"{requested_word} With {benefit_word} Confidence",
        f"{benefit_word} Made Simple For Every Team",
        f"{product_word} Delivers {requested_word} At Scale",
        f"Move Forward With {benefit_word} Confidence",
        f"Trust {product_word} For {requested_word} Results",
        f"Smarter {benefit_word} For Confident Teams",
        f"{requested_word} Clarity Starts With {product_word}",
    ]

    candidates = []
    seen = set()

    for template in templates:
        tagline = _fit_to_word_range(template, brief, fillers)
        normalized = tagline.lower().strip()

        if normalized not in seen:
            seen.add(normalized)
            candidates.append(tagline)

        if len(candidates) == n:
            break

    return candidates