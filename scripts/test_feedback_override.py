from backend.app.feedback import (
    record_analyst_feedback,
)

from backend.app.memory import (
    recall_experience,
)

from backend.app.tools import (
    alert_context,
)


# =========================================================
# GET ALERT
# =========================================================

alert = alert_context("ALT-001")

if alert is None:
    raise ValueError("ALT-001 was not found")


# =========================================================
# SIMULATED AGENT RECOMMENDATION
# =========================================================

candidate_verdict = {
    "verdict": "Likely Benign",
    "confidence": 0.90,
}


# =========================================================
# ANALYST CORRECTION
# =========================================================

final_verdict = {
    "verdict": "Investigate",
}


# =========================================================
# RECORD ANALYST OVERRIDE
# =========================================================

result = record_analyst_feedback(
    alert=alert,
    candidate_verdict=candidate_verdict,
    final_verdict=final_verdict,
    action="override",
    analyst_reason=(
        "The analyst identified an additional suspicious "
        "indicator that was not present in the historical "
        "Veeam benign exception."
    ),
)


print("ANALYST OVERRIDE TEST")
print("---------------------")
print()

print("FEEDBACK RESULT:")
print(result)

print()


# =========================================================
# RECALL THE NEWLY STORED OVERRIDE
# =========================================================

query = """
Find analyst corrections for ALT-001.

Look for:
- analyst override
- original Likely Benign recommendation
- corrected Investigate decision
- suspicious indicator
"""

memories = recall_experience(query)


print(
    f"HINDSIGHT MEMORIES FOUND: "
    f"{len(memories)}"
)

print()


for index, memory in enumerate(
    memories,
    start=1,
):
    print(f"MEMORY {index}:")
    print(memory["text"])
    print()


# =========================================================
# VERIFY OVERRIDE WAS RECALLED
# =========================================================

override_found = any(
    (
        "overrode" in memory["text"].lower()
        and "ALT-001" in memory["text"]
        and "Investigate" in memory["text"]
    )
    for memory in memories
)


assert override_found is True


# =========================================================
# FINAL RESULT
# =========================================================

print("=" * 60)
print("ANALYST OVERRIDE RETAIN + RECALL TEST PASSED")
print("=" * 60)