from agents.prompts import (
    build_art_director_prompt,
    build_copywriter_prompt,
    build_prompt_summary,
)
from schemas import AdBrief


brief = AdBrief(
    product_name="FitFuel Protein Bar",
    category="Food",
    usp="20g protein, zero sugar",
    tone="Witty",
    ad_format="Instagram post (1080×1080)",
    product_description="High-protein snack with no added sugar",
    audience="Gym-goers and busy professionals aged 18–25",
    objective="Product launch",
    cta="Buy now",
    visual_style="Photorealistic",
    color_mood="Warm",
    brand_hex="#F97316",
    tagline_length="Short (3–5 words)",
    text_position="Top",
    include_words=["fuel", "protein"],
    avoid_words=["guilt", "cheat"],
)

print("\n--- UI SUMMARY ---")
print(build_prompt_summary(brief))

print("\n--- COPYWRITER PROMPT ---")
print(build_copywriter_prompt(brief, n=5))

print("\n--- ART DIRECTOR PROMPT ---")
print(build_art_director_prompt(brief))