from schemas import AdBrief


def build_copywriter_prompt(brief: AdBrief, n: int = 5) -> str:
    """
    Build a strict prompt for the tagline-generation model.
    """

    min_words, max_words = brief.tagline_word_range

    include_instruction = (
        f"Naturally include one or more of these words/themes when appropriate: "
        f"{', '.join(brief.include_words)}."
        if brief.include_words
        else "No required words or themes."
    )

    avoid_instruction = (
        f"Do not use these words/themes: {', '.join(brief.avoid_words)}."
        if brief.avoid_words
        else "Avoid unsupported claims, clichés, and excessive punctuation."
    )

    cta_instruction = (
        f"CTA context: {brief.cta.value}."
        if brief.cta.value != "None"
        else "Do not include a call to action."
    )

    offer_instruction = (
        f"Campaign objective: {brief.objective}."
    )

    return f"""You are AdSpark's specialist advertising copywriter.

Generate exactly {n} distinct, concise, brand-safe taglines.
Return only a numbered list. Do not add explanations.

Product: {brief.product_name}
Category: {brief.category.value}
Description: {brief.product_description or "Not provided"}
USP: {brief.usp}
Audience: {brief.audience}
{offer_instruction}
Tone: {brief.tone.value}
Language: {brief.language}
Target length: {min_words}–{max_words} words.
{cta_instruction}
{include_instruction}
{avoid_instruction}

Rules:
- Every tagline must contain {min_words}–{max_words} words.
- Make the product benefit or USP recognizable when natural.
- Match the requested tone.
- Do not use hashtags, emojis, URLs, quotation marks, or more than one exclamation mark.
- Do not mention competitors or make unverifiable claims.
"""


def build_art_director_prompt(brief: AdBrief) -> str:
    """
    Build an image-model prompt for an ad background.
    The final tagline is added later by Pillow, not the image model.
    """

    width, height = brief.dimensions

    color_instruction = (
        f"Use {brief.brand_hex} as a subtle brand accent color."
        if brief.brand_hex
        else f"Use a {brief.color_mood.value.lower()} palette."
    )

    position = (
        "a composition chosen automatically by the art director"
        if brief.text_position.value == "Auto"
        else f"clear negative space at the {brief.text_position.value.lower()}"
    )

    return f"""Create an original, polished advertising background image.

Product: {brief.product_name}
Category: {brief.category.value}
Description: {brief.product_description or brief.usp}
Audience: {brief.audience}
Campaign objective: {brief.objective}
Visual style: {brief.visual_style.value}
Color direction: {color_instruction}
Canvas: {width}x{height}px for {brief.format_key}
Layout: Reserve {position} for a headline overlay.

Requirements:
- Make the product or relevant visual subject prominent.
- Keep the headline zone uncluttered with strong visual contrast.
- Do not generate any words, letters, logos, watermarks, labels, signs, or readable text.
- Use a professional commercial advertising composition.
"""


def build_prompt_summary(brief: AdBrief) -> str:
    """
    Generate short UI text describing what AdSpark will create.
    """

    position = (
        "automatically selected headline placement"
        if brief.text_position.value == "Auto"
        else f"headline placed at the {brief.text_position.value.lower()}"
    )

    return (
        f"A {brief.tone.value.lower()}, "
        f"{brief.color_mood.value.lower()}-toned "
        f"{brief.format_key.replace('_', ' ')} ad for "
        f"{brief.product_name}, targeting {brief.audience}. "
        f"The campaign highlights “{brief.usp}” with {position}."
    )