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
    tagline_length="Short (3–5 words)",
    include_words=["fuel", "protein"],
    avoid_words=["guilt", "cheat"],
    num_variants=3,
)

result = run_copywriter_critic_loop(brief)

print("\n--- FINAL RESULT ---")
print("Final tagline:", result["final_tagline"])
print("Final score:", result["final_score"])
print("Rewrite attempts:", result["rewrite_attempts"])

print("\n--- AGENT TRACE ---")
for step_number, step in enumerate(result["trace"], start=1):
    print(f"\n{step_number}. {step['agent']} -> {step['action']}")
    print(step["details"])