from agents.composer import compose_banner
from agents.workflow import run_copywriter_critic_loop
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
    num_variants=3,
)

workflow_result = run_copywriter_critic_loop(brief)

banner_result = compose_banner(
    brief=brief,
    tagline=workflow_result["final_tagline"],
)

print("\n--- BANNER CREATED ---")
print("Tagline:", banner_result["tagline"])
print("Wrapped tagline:", banner_result["wrapped_tagline"])
print("Canvas:", banner_result["dimensions"])
print("Output file:", banner_result["output_path"])
print("Tagline characters:", banner_result["tagline_character_count"])