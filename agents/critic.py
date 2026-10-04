import re

from schemas import AdBrief


BANNED_TERMS = {
    "guaranteed",
    "cure",
    "risk-free",
    "best ever",
    "miracle",
    "instant results",
}

GENERIC_STARTERS = {
    "power your",
    "unlock your",
    "discover the",
    "experience the",
}

AWKWARD_PATTERNS = [
    r"^[a-zA-Z]+,\s+(meets|makes|brings|gives|powers)\b",
    r"\bwith\s+with\b",
    r"\bthe\s+the\b",
    r"\b[a-zA-Z]+,\s+(meets|makes|brings)\b",
]


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", value.lower()).strip()


def count_words(tagline: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", tagline))


def contains_banned_term(tagline: str) -> bool:
    normalized = normalize_text(tagline)

    return any(
        banned_term in normalized
        for banned_term in BANNED_TERMS
    )


def has_awkward_copy(tagline: str) -> bool:
    normalized = tagline.lower().strip()

    if any(
        re.search(pattern, normalized)
        for pattern in AWKWARD_PATTERNS
    ):
        return True

    if tagline.count(",") > 1:
        return True

    if tagline.strip().endswith(","):
        return True

    return False


def is_generic(tagline: str) -> bool:
    normalized = normalize_text(tagline)

    return any(
        normalized.startswith(starter)
        for starter in GENERIC_STARTERS
    )


def passes_hard_quality_gates(
    tagline: str,
    brief: AdBrief,
) -> tuple[bool, list[str]]:
    """
    Rules that must pass before a tagline can become the final banner text.
    """

    min_words, max_words = brief.tagline_word_range
    word_count = count_words(tagline)
    normalized = normalize_text(tagline)

    issues = []

    if not min_words <= word_count <= max_words:
        issues.append(
            f"Must contain {min_words}–{max_words} words; found {word_count}."
        )

    if len(tagline) > 48:
        issues.append(
            f"Too long for reliable banner layout: {len(tagline)} characters."
        )

    if tagline.count("!") > 1:
        issues.append("Contains excessive exclamation marks.")

    if contains_banned_term(tagline):
        issues.append("Contains an unsupported or unsafe marketing claim.")

    if any(
        normalize_text(word) in normalized
        for word in brief.avoid_words
    ):
        issues.append("Contains a word or theme the user asked to avoid.")

    if has_awkward_copy(tagline):
        issues.append("Contains awkward grammar or punctuation.")

    return len(issues) == 0, issues


def score_tagline(tagline: str, brief: AdBrief) -> dict:
    """
    Score one candidate using transparent rules.

    Soft score, 0–100:
    - Length compliance: 25
    - USP relevance: 25
    - Requested theme fit: 15
    - Brand safety: 20
    - Readability: 15

    Hard gates prevent unusable text from being selected even if its
    semantic score is high.
    """

    min_words, max_words = brief.tagline_word_range
    word_count = count_words(tagline)
    normalized = normalize_text(tagline)

    scores = {
        "length": 0,
        "usp_relevance": 0,
        "tone_fit": 0,
        "brand_safety": 0,
        "readability": 0,
    }

    feedback = []

    # 25 points: selected word range
    if min_words <= word_count <= max_words:
        scores["length"] = 25
    else:
        feedback.append(
            f"Use {min_words}–{max_words} words; found {word_count}."
        )

    # 25 points: recognizable USP term
    usp_terms = [
        term
        for term in re.findall(r"[a-zA-Z]+", brief.usp.lower())
        if len(term) >= 4 and term not in {"with", "zero", "added"}
    ]

    matching_usp_terms = [
        term for term in usp_terms if term in normalized
    ]

    if matching_usp_terms:
        scores["usp_relevance"] = 25
    else:
        feedback.append(
            "Make the core product benefit or USP more recognizable."
        )

    # 15 points: requested user words/themes
    if brief.include_words:
        includes_requested_theme = any(
            normalize_text(word) in normalized
            for word in brief.include_words
        )

        if includes_requested_theme:
            scores["tone_fit"] = 15
        else:
            feedback.append(
                "Naturally incorporate a requested word or theme."
            )
    else:
        scores["tone_fit"] = 15

    # 20 points: safety and exclusion compliance
    has_banned_term = contains_banned_term(tagline)
    has_avoid_word = any(
        normalize_text(word) in normalized
        for word in brief.avoid_words
    )

    if not has_banned_term and not has_avoid_word:
        scores["brand_safety"] = 20
    else:
        if has_banned_term:
            feedback.append(
                "Remove unsupported or unsafe marketing claims."
            )

        if has_avoid_word:
            feedback.append(
                "Remove words or themes the user asked to avoid."
            )

    # 15 points: readability and basic copy quality
    readable_length = len(tagline) <= 48
    controlled_punctuation = tagline.count("!") <= 1
    awkward_copy = has_awkward_copy(tagline)
    generic_copy = is_generic(tagline)

    if (
        readable_length
        and controlled_punctuation
        and not awkward_copy
        and not generic_copy
    ):
        scores["readability"] = 15
    else:
        if not readable_length:
            feedback.append("Make the tagline shorter.")

        if not controlled_punctuation:
            feedback.append("Reduce excessive punctuation.")

        if awkward_copy:
            feedback.append(
                "Rewrite for natural grammar and punctuation."
            )

        if generic_copy:
            feedback.append(
                "Replace generic advertising language with a more distinctive phrase."
            )

    total_score = sum(scores.values())

    passes_hard_gates, hard_gate_issues = passes_hard_quality_gates(
        tagline,
        brief,
    )

    return {
        "tagline": tagline,
        "word_count": word_count,
        "character_count": len(tagline),
        "scores": scores,
        "total_score": total_score,
        "feedback": feedback,
        "passes_hard_gates": passes_hard_gates,
        "hard_gate_issues": hard_gate_issues,
        "passes_quality_gate": (
            total_score >= 70 and passes_hard_gates
        ),
    }


def rank_taglines(candidates: list[str], brief: AdBrief) -> list[dict]:
    """
    Score candidates and rank highest to lowest.
    """

    scored = [
        score_tagline(tagline, brief)
        for tagline in candidates
    ]

    return sorted(
        scored,
        key=lambda item: item["total_score"],
        reverse=True,
    )


def select_best_tagline(candidates: list[str], brief: AdBrief) -> dict:
    """
    Prefer the highest-ranked candidate that passes hard gates.

    If all candidates fail, return the top score so its feedback can drive
    the Copywriter rewrite request.
    """

    ranked = rank_taglines(candidates, brief)

    if not ranked:
        raise ValueError(
            "The Copywriter agent returned no tagline candidates."
        )

    valid_candidates = [
        candidate
        for candidate in ranked
        if candidate["passes_quality_gate"]
    ]

    return valid_candidates[0] if valid_candidates else ranked[0]
