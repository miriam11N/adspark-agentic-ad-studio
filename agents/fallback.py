import re

from schemas import AdBrief, TaglineLength


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def _meaningful_words(text: str) -> list[str]:
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
        "every",
        "team",
        "made",
        "simple",
        "today",
        "everywhere",
    }

    return [
        word.title()
        for word in _words(text)
        if len(word) >= 4 and word not in stop_words
    ]


def _is_allowed(word: str, brief: AdBrief) -> bool:
    normalized = word.lower().strip()

    return not any(
        normalize_avoid.lower().strip() == normalized
        for normalize_avoid in brief.avoid_words
    )


def _first_allowed(words: list[str], fallback: str, brief: AdBrief) -> str:
    for word in words:
        if _is_allowed(word, brief):
            return word

    return fallback


def build_safe_fallback_tagline(brief: AdBrief) -> str:
    """
    Return a deterministic, banner-safe tagline appropriate for the user's
    selected word range. It must pass the Critic's hard gates.

    These are fallback patterns only. In production, the Copywriter model
    should generate the final phrase; this prevents broken text from reaching
    the Pillow composer when model output fails validation.
    """

    source_words = []

    for include_word in brief.include_words:
        source_words.extend(_meaningful_words(include_word))

    source_words.extend(_meaningful_words(brief.usp))
    source_words.extend(_meaningful_words(brief.product_name))

    primary = _first_allowed(
        source_words,
        fallback="Smart",
        brief=brief,
    )

    secondary = _first_allowed(
        source_words[1:],
        fallback="Results",
        brief=brief,
    )

    short_templates = [
        f"{primary} Made Clear",
        f"{primary} Builds Confidence",
        f"Clear {primary} Starts Here",
        f"{secondary} With Confidence",
    ]

    medium_templates = [
        f"{primary} Built For Confident Decisions Today",
        f"Make {primary} Clear For Every Team",
        f"{secondary} That Keeps Teams Moving Forward",
        f"Confident Teams Choose {primary} Every Day",
    ]

    long_templates = [
    f"{primary} Builds Confidence For Smarter Decisions Every Day",
    f"Clear {primary} Helps Teams Move Forward With Confidence",
    f"{secondary} Makes Every Decision Clear And Confident",
    f"Better Decisions Start With {primary} And Confidence",
]

    if brief.tagline_length == TaglineLength.SHORT:
        templates = short_templates
    elif brief.tagline_length == TaglineLength.MEDIUM:
        templates = medium_templates
    else:
        templates = long_templates

    min_words, max_words = brief.tagline_word_range

    for candidate in templates:
        candidate_words = candidate.split()

        if not min_words <= len(candidate_words) <= max_words:
            continue

        if len(candidate) > 48:
            continue

        candidate_has_avoid_word = any(
            avoid_word.lower() in candidate.lower()
            for avoid_word in brief.avoid_words
        )

        if not candidate_has_avoid_word:
            return candidate

    # Conservative emergency fallback.
    # Usually only reached if user avoids many common terms.
    emergency_templates = {
        TaglineLength.SHORT: "Smart Clear Results",
        TaglineLength.MEDIUM: "Smart Results For Confident Daily Decisions",
        TaglineLength.LONG: (
            "Smart Results For Clear Confident Decisions Every Single Day"
        ),
    }

    return emergency_templates[brief.tagline_length]
