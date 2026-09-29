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


final_verdict = {
    "verdict": "Likely Benign",
}


# =========================================================
# RECORD ANALYST APPROVAL
# =========================================================

result = record_analyst_feedback(
    alert=alert,
    candidate_verdict=candidate_verdict,
    final_verdict=final_verdict,
    action="approve",
    analyst_reason=(
        "Confirmed that the encoded PowerShell activity "
        "came from the approved Veeam backup process during "
        "the scheduled backup window."
    ),
)


print("ANALYST APPROVAL TEST")
print("---------------------")
print()

print("FEEDBACK RESULT:")
print(result)

print()


# =========================================================
# RECALL THE NEWLY STORED FEEDBACK
# =========================================================

query = """
Find the analyst feedback for ALT-001.

Look for:
- analyst approval
- Likely Benign
- Veeam backup process
- scheduled backup window
- encoded PowerShell
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
    print(
        f"MEMORY {index}:"
    )
    print(
        memory["text"]
    )
    print()


# =========================================================
# VERIFY THAT APPROVAL WAS RECALLED
# =========================================================

approval_found = any(
    (
        "approved" in memory["text"].lower()
        and "ALT-001" in memory["text"]
    )
    for memory in memories
)


assert approval_found is True


# =========================================================
# FINAL RESULT
# =========================================================

print("=" * 60)
print("ANALYST APPROVAL RETAIN + RECALL TEST PASSED")
print("=" * 60)