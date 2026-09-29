from backend.app.guardrails import (
    apply_benign_memory_guardrail,
)

from backend.app.memory import recall_experience

from backend.app.tools import (
    alert_context,
    asset_lookup,
    user_lookup,
)


def get_memories():
    query = """
SOC alert triage.

Find memories about:
- Veeam backup service
- encoded PowerShell
- historical Likely Benign decisions
- backup server
- svc-veeam
- Veeam.Backup.Service.exe
- approved backup schedule
- Veeam decommissioning
- retirement of the old exception
- superseding environment changes
"""

    return recall_experience(query)


def build_candidate():
    return {
        "verdict": "Likely Benign",
        "confidence": 0.90,
        "reasoning": (
            "Historical memory appears to support "
            "this activity."
        ),
        "matched_conditions": [],
        "mismatched_conditions": [],
        "memory_evidence": [],
    }


def test_alert(alert_id, memories):
    alert = alert_context(alert_id)

    if alert is None:
        raise ValueError(
            f"Alert {alert_id} was not found"
        )

    asset = asset_lookup(alert["asset_id"])

    if asset is None:
        raise ValueError(
            f"Asset {alert['asset_id']} was not found"
        )

    account = user_lookup(alert["account_id"])

    if account is None:
        raise ValueError(
            f"Account {alert['account_id']} was not found"
        )

    candidate = build_candidate()

    result = apply_benign_memory_guardrail(
        alert,
        asset,
        account,
        memories,
        candidate,
    )

    print()
    print("=" * 70)
    print(f"TESTING {alert_id}")
    print("=" * 70)

    print()
    print("Alert:")
    print(f"  Asset: {alert['asset_id']}")
    print(f"  Account: {alert['account_id']}")
    print(f"  Severity: {alert['severity']}")
    print(f"  Parent: {alert['parent_process']}")
    print(f"  Timestamp: {alert['timestamp']}")

    print()
    print("FINAL GUARDRAIL RESULT:")
    print(result)

    return result


# =========================================================
# GET HINDSIGHT MEMORIES
# =========================================================

memories = get_memories()

print()
print(
    f"Hindsight memories retrieved: "
    f"{len(memories)}"
)


# =========================================================
# TEST 1 — MATCHING HISTORICAL SCENARIO
# =========================================================

result_001 = test_alert(
    "ALT-001",
    memories,
)

assert result_001["verdict"] == "Likely Benign"

assert result_001["guardrail_override"] is False


# =========================================================
# TEST 2 — NON-MATCHING SCENARIO
# =========================================================

result_003 = test_alert(
    "ALT-003",
    memories,
)

assert result_003["verdict"] == "Investigate"

assert result_003["guardrail_override"] is True


# =========================================================
# FINAL RESULT
# =========================================================

print()
print("=" * 70)
print("BENIGN MEMORY GUARDRAIL TEST PASSED")
print("=" * 70)