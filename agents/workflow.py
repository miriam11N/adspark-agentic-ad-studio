from agents.copywriter import (
    generate_mock_rewrite_taglines,
    generate_mock_taglines,
)
from agents.critic import rank_taglines, select_best_tagline
from agents.fallback import build_safe_fallback_tagline
from schemas import AdBrief


QUALITY_THRESHOLD = 70
MAX_REWRITE_ATTEMPTS = 1


def make_rewrite_instruction(ranked_candidates: list[dict]) -> str:
    """
    Convert the Critic's feedback into a compact Copywriter instruction.
    """

    best_candidate = ranked_candidates[0]
    feedback = best_candidate["feedback"]
    hard_gate_issues = best_candidate["hard_gate_issues"]

    all_feedback = feedback + hard_gate_issues

    if not all_feedback:
        return (
            "Create a more distinctive alternative while preserving the "
            "requested tone, USP, and word-count range."
        )

    return " ".join(all_feedback)


def generate_rewrite_candidates(
    brief: AdBrief,
    rewrite_instruction: str,
    n: int = 5,
) -> list[str]:
    """
    Temporary wrapper for the brief-aware mock rewrite Copywriter.

    Later replace this function with an API or fine-tuned LoRA model call.
    """

    return generate_mock_rewrite_taglines(
        brief=brief,
        rewrite_instruction=rewrite_instruction,
        n=n,
    )


def choose_valid_or_fallback(
    candidates: list[str],
    brief: AdBrief,
) -> tuple[dict, bool]:
    """
    Return the best valid candidate.

    When every candidate fails a hard quality gate, create and validate a
    deterministic banner-safe fallback instead of returning bad text.
    """

    winner = select_best_tagline(candidates, brief)

    if winner["passes_quality_gate"]:
        return winner, False

    fallback_tagline = build_safe_fallback_tagline(brief)
    fallback_winner = select_best_tagline([fallback_tagline], brief)

    return fallback_winner, True


def run_copywriter_critic_loop(brief: AdBrief) -> dict:
    """
    AdSpark's Copywriter-Critic agentic loop.

    1. Generate candidates.
    2. Score/rank candidates.
    3. Immediately select a passing candidate, if one exists.
    4. Otherwise ask the Copywriter for one rewrite batch.
    5. If rewrites still fail, generate a deterministic safe fallback.
    """

    trace = []

    initial_candidates = generate_mock_taglines(
        brief=brief,
        n=brief.num_variants + 2,
    )

    initial_ranking = rank_taglines(initial_candidates, brief)
    initial_winner = select_best_tagline(initial_candidates, brief)

    trace.append(
        {
            "agent": "Copywriter",
            "action": "generated_initial_candidates",
            "details": initial_candidates,
        }
    )

    trace.append(
        {
            "agent": "Critic",
            "action": "ranked_initial_candidates",
            "details": initial_ranking,
        }
    )

    if initial_winner["passes_quality_gate"]:
        trace.append(
            {
                "agent": "Critic",
                "action": "selected_initial_winner",
                "details": {
                    "tagline": initial_winner["tagline"],
                    "score": initial_winner["total_score"],
                    "reason": (
                        "Candidate passed the score threshold and all "
                        "hard quality gates."
                    ),
                },
            }
        )

        return {
            "final_tagline": initial_winner["tagline"],
            "final_score": initial_winner["total_score"],
            "rewrite_attempts": 0,
            "used_fallback": False,
            "final_ranking": initial_ranking,
            "trace": trace,
        }

    rewrite_instruction = make_rewrite_instruction(initial_ranking)

    trace.append(
        {
            "agent": "Critic",
            "action": "requested_rewrite",
            "details": {
                "failed_candidate": initial_winner["tagline"],
                "failed_score": initial_winner["total_score"],
                "rewrite_instruction": rewrite_instruction,
            },
        }
    )

    rewrite_candidates = generate_rewrite_candidates(
        brief=brief,
        rewrite_instruction=rewrite_instruction,
        n=brief.num_variants + 2,
    )

    rewrite_ranking = rank_taglines(rewrite_candidates, brief)
    final_winner, used_fallback = choose_valid_or_fallback(
        rewrite_candidates,
        brief,
    )

    trace.append(
        {
            "agent": "Copywriter",
            "action": "generated_rewrite_candidates",
            "details": rewrite_candidates,
        }
    )

    if used_fallback:
        trace.append(
            {
                "agent": "Fallback",
                "action": "generated_banner_safe_tagline",
                "details": {
                    "tagline": final_winner["tagline"],
                    "reason": (
                        "No rewrite candidate passed all hard quality gates."
                    ),
                    "score": final_winner["total_score"],
                },
            }
        )

    trace.append(
        {
            "agent": "Critic",
            "action": "selected_final_winner",
            "details": {
                "tagline": final_winner["tagline"],
                "score": final_winner["total_score"],
                "passes_quality_gate": final_winner[
                    "passes_quality_gate"
                ],
                "feedback": final_winner["feedback"],
                "hard_gate_issues": final_winner["hard_gate_issues"],
                "used_fallback": used_fallback,
            },
        }
    )

    return {
        "final_tagline": final_winner["tagline"],
        "final_score": final_winner["total_score"],
        "rewrite_attempts": MAX_REWRITE_ATTEMPTS,
        "used_fallback": used_fallback,
        "final_ranking": rewrite_ranking,
        "trace": trace,
    }
