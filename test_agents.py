from agents.copywriter import generate_mock_taglines
from agents.critic import rank_taglines, select_best_tagline
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
    tagline_length="Short (3–5 words)",
    include_words=["fuel", "protein"],
    avoid_words=["guilt", "cheat"],
)

candidates = generate_mock_taglines(brief, n=5)
ranked = rank_taglines(candidates, brief)
winner = select_best_tagline(candidates, brief)

print("\n--- COPYWRITER CANDIDATES ---")
for index, tagline in enumerate(candidates, start=1):
    print(f"{index}. {tagline}")

print("\n--- CRITIC RANKING ---")
for index, result in enumerate(ranked, start=1):
    print(f"\n{index}. {result['tagline']}")
    print(f"   Score: {result['total_score']}/100")
    print(f"   Word count: {result['word_count']}")
    print(f"   Details: {result['scores']}")
    print(
        "   Feedback:",
        "; ".join(result["feedback"]) if result["feedback"] else "Passed",
    )

print("\n--- SELECTED TAGLINE ---")
print(winner["tagline"])
print(f"Score: {winner['total_score']}/100")
print(f"Quality gate passed: {winner['passes_quality_gate']}")