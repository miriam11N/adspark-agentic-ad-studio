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
    include_words=["fuel", "protein", "Fuel"],
    avoid_words=["guilt", "cheat"],
)

print("\nValidated brief:\n")
print(brief.model_dump(mode="json"))

print("\nDerived values:")
print("Format key:", brief.format_key)
print("Dimensions:", brief.dimensions)
print("Tagline range:", brief.tagline_word_range)
print("Include words:", brief.include_words)