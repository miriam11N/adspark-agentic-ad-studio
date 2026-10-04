from agents.workflow import run_copywriter_critic_loop
from schemas import AdBrief


brief = AdBrief(
    product_name="Nimbus Workflow Platform",
    category="Tech",
    usp="Automates complex compliance reporting",
    tone="Luxury",
    ad_format="Web banner (1200×628)",
    audience="Enterprise risk teams",
    objective="Brand awareness",
    tagline_length="Long (7–10 words)",
    include_words=["compliance", "confidence"],
    avoid_words=["power", "fuel", "protein", "sugar"],
    num_variants=3,
)

result = run_copywriter_critic_loop(brief)

print("\n--- REWRITE TEST RESULT ---")
print("Final tagline:", result["final_tagline"])
print("Final score:", result["final_score"])
print("Rewrite attempts:", result["rewrite_attempts"])
print("Used fallback:", result["used_fallback"])

print("\n--- AGENT TRACE ---")
for step_number, step in enumerate(result["trace"], start=1):
    print(f"\n{step_number}. {step['agent']} -> {step['action']}")
    print(step["details"])