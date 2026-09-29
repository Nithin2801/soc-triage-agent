from backend.app.guardrails import (
    check_newer_memory_conflict,
    check_effective_memory_change,
)

from backend.app.memory import recall_experience


def get_memories():
    query = """
SOC alert triage.

Find memories about:
- Veeam backup service
- encoded PowerShell
- the historical benign exception
- decommissioning
- retirement or superseding of that exception

Return relevant historical and environment-change memories.
"""

    return recall_experience(query)


# =========================================================
# GET HINDSIGHT MEMORIES
# =========================================================

memories = get_memories()

print("NEWER MEMORY CONFLICT TEST")
print("--------------------------")
print()

print(
    f"Hindsight memories retrieved: "
    f"{len(memories)}"
)

print()


# =========================================================
# TEST 1 — ALERT BEFORE THE CHANGE
# =========================================================

old_alert = {
    "alert_id": "TEST-BEFORE-CHANGE",
    "timestamp": "2026-09-28T02:00:00",
}

old_result = check_newer_memory_conflict(
    old_alert,
    memories,
)

print("ALERT BEFORE CHANGE:")
print(old_alert)

print()

print("NEWER MEMORY CONFLICT RESULT:")
print(old_result)

print()

assert old_result["conflict"] is True


# =========================================================
# TEST 2 — ALERT AFTER THE CHANGE
# =========================================================

new_alert = {
    "alert_id": "TEST-AFTER-CHANGE",
    "timestamp": "2026-09-30T02:00:00",
}

new_result = check_newer_memory_conflict(
    new_alert,
    memories,
)

print("ALERT AFTER CHANGE:")
print(new_alert)

print()

print("NEWER MEMORY CONFLICT RESULT:")
print(new_result)

print()


# =========================================================
# TEST 3 — CHECK WHETHER CHANGE WAS ALREADY EFFECTIVE
# =========================================================

print("=" * 60)
print("EFFECTIVE CHANGE TEST")
print("=" * 60)


# ---------------------------------------------------------
# Alert BEFORE the change
# ---------------------------------------------------------

before_result = check_effective_memory_change(
    old_alert,
    memories,
)

print()

print("BEFORE CHANGE:")
print(before_result)

print()

assert before_result["effective_change"] is False


# ---------------------------------------------------------
# Alert AFTER the change
# ---------------------------------------------------------

after_result = check_effective_memory_change(
    new_alert,
    memories,
)

print("AFTER CHANGE:")
print(after_result)

print()

assert after_result["effective_change"] is True


# =========================================================
# FINAL RESULT
# =========================================================

print("=" * 60)
print("EFFECTIVE CHANGE TEST PASSED")
print("=" * 60)

print()

print("=" * 60)
print("ALL TEMPORAL MEMORY TESTS PASSED")
print("=" * 60)