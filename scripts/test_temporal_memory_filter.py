from backend.app.reasoner import (
    _filter_temporally_valid_memories,
    _select_relevant_memories,
)


BEFORE_CHANGE_ALERT = {
    "alert_id": "TEMPORAL-BEFORE-001",
    "alert_type": "Encoded PowerShell",
    "technique_id": "T1059.001",
    "severity": "medium",
    "asset_id": "BKP-SRV-02",
    "account_id": "svc-veeam",
    "timestamp": "2026-09-28T02:05:00",
    "parent_process": "Veeam.Backup.Service.exe",
    "command_pattern": "Encoded PowerShell command",
}


AFTER_CHANGE_ALERT = {
    "alert_id": "TEMPORAL-AFTER-001",
    "alert_type": "Encoded PowerShell",
    "technique_id": "T1059.001",
    "severity": "medium",
    "asset_id": "BKP-SRV-02",
    "account_id": "svc-veeam",
    "timestamp": "2026-09-29T02:05:00",
    "parent_process": "Veeam.Backup.Service.exe",
    "command_pattern": "Encoded PowerShell command",
}


TEST_MEMORIES = [
    {
        "type": "world",
        "text": (
            "Encoded PowerShell activity on BKP-SRV-02 using "
            "svc-veeam and Veeam.Backup.Service.exe was classified "
            "as Likely Benign on 2026-09-28."
        ),
    },
    {
        "type": "world",
        "text": (
            "Veeam backup service decommissioned from the environment. "
            "When: 2026-09-29. "
            "The previous exception was superseded."
        ),
    },
    {
        "type": "world",
        "text": (
            "Future encoded PowerShell activity must not be classified "
            "as Likely Benign based on historical Veeam patterns. "
            "The exception is retired on 2026-09-29."
        ),
    },
]


print("=" * 70)
print("TEMPORAL MEMORY FILTER TEST")
print("=" * 70)


# ============================================================
# TEST 1 — ALERT BEFORE ENVIRONMENT CHANGE
# ============================================================

print()
print("TEST 1: ALERT BEFORE ENVIRONMENT CHANGE")
print("-" * 70)

before_valid = _filter_temporally_valid_memories(
    BEFORE_CHANGE_ALERT,
    TEST_MEMORIES,
)

print(
    f"Memories before filtering: "
    f"{len(TEST_MEMORIES)}"
)

print(
    f"Memories after filtering: "
    f"{len(before_valid)}"
)

for memory in before_valid:
    print()
    print(memory["text"])


before_text = [
    memory["text"]
    for memory in before_valid
]


assert any(
    "2026-09-28" in text
    for text in before_text
), (
    "Historical 2026-09-28 memory should remain "
    "for a 2026-09-28 alert."
)


assert not any(
    "2026-09-29" in text
    for text in before_text
), (
    "Future 2026-09-29 memories must NOT influence "
    "a 2026-09-28 alert."
)


print()
print("BEFORE-CHANGE TEMPORAL ASSERTION PASSED")


# ============================================================
# TEST 2 — ALERT ON ENVIRONMENT CHANGE DATE
# ============================================================

print()
print("TEST 2: ALERT ON ENVIRONMENT CHANGE DATE")
print("-" * 70)

after_valid = _filter_temporally_valid_memories(
    AFTER_CHANGE_ALERT,
    TEST_MEMORIES,
)

print(
    f"Memories before filtering: "
    f"{len(TEST_MEMORIES)}"
)

print(
    f"Memories after filtering: "
    f"{len(after_valid)}"
)

for memory in after_valid:
    print()
    print(memory["text"])


after_text = [
    memory["text"]
    for memory in after_valid
]


assert any(
    "2026-09-28" in text
    for text in after_text
), (
    "Historical memory should remain available."
)


assert any(
    "2026-09-29" in text
    for text in after_text
), (
    "The environment change should be available "
    "for an alert occurring on 2026-09-29."
)


print()
print("AFTER-CHANGE TEMPORAL ASSERTION PASSED")


# ============================================================
# TEST 3 — RELEVANCE SELECTION MUST NOT REINTRODUCE
#           FUTURE MEMORIES
# ============================================================

print()
print("TEST 3: TEMPORAL FILTER + RELEVANCE SELECTION")
print("-" * 70)

selected_before = _select_relevant_memories(
    BEFORE_CHANGE_ALERT,
    before_valid,
)

selected_before_text = [
    memory["text"]
    for memory in selected_before
]


assert not any(
    "2026-09-29" in text
    for text in selected_before_text
), (
    "Evidence selection must not reintroduce "
    "future memories."
)


print(
    f"Relevant memories selected for the "
    f"2026-09-28 alert: {len(selected_before)}"
)


print()
print("NO FUTURE MEMORY LEAKAGE DETECTED")


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 70)
print("ALL TEMPORAL MEMORY ASSERTIONS PASSED")
print("=" * 70)

print()
print("TEMPORAL MEMORY FILTER TEST PASSED")
print("=" * 70)