from backend.app.decision_engine import (
    make_final_decision,
)


def print_result(result):
    alert = result["alert"]
    candidate = result["candidate_verdict"]
    final = result["final_verdict"]

    print()
    print("=" * 70)
    print(
        f"ALERT {alert['alert_id']}"
    )
    print("=" * 70)

    print()

    print("ALERT CONTEXT:")
    print(
        f"  Type: {alert['alert_type']}"
    )
    print(
        f"  Severity: {alert['severity']}"
    )
    print(
        f"  Asset: {alert['asset_id']}"
    )
    print(
        f"  Account: {alert['account_id']}"
    )
    print(
        f"  Parent: {alert['parent_process']}"
    )
    print(
        f"  Time: {alert['timestamp']}"
    )

    print()

    print(
        "HINDSIGHT MEMORIES:"
    )
    print(
        f"  {len(result['memories'])} memories recalled"
    )

    print()

    print("CANDIDATE VERDICT:")
    print(
        f"  {candidate['verdict']}"
    )

    print(
        f"  Confidence: "
        f"{candidate['confidence']}"
    )

    print()

    print("FINAL VERDICT:")
    print(
        f"  {final['verdict']}"
    )

    print()

    print("GUARDRAIL OVERRIDE:")
    print(
        f"  {final.get('guardrail_override')}"
    )

    print()

    print("GUARDRAIL REASON:")
    print(
        f"  {final.get('guardrail_reason')}"
    )


# =========================================================
# TEST 1 — Matching benign scenario
# =========================================================

result_001 = make_final_decision(
    "ALT-001"
)

print_result(result_001)

assert result_001["final_verdict"]["verdict"] == (
    "Likely Benign"
)


# =========================================================
# TEST 2 — Non-matching historical scenario
# =========================================================

result_003 = make_final_decision(
    "ALT-003"
)

print_result(result_003)

assert result_003["final_verdict"]["verdict"] in (
    "Investigate",
    "Escalate",
)


# =========================================================
# TEST 3 — Critical alert
# =========================================================

result_004 = make_final_decision(
    "ALT-004"
)

print_result(result_004)

assert result_004["final_verdict"]["verdict"] == (
    "Escalate"
)


# =========================================================
# FINAL RESULT
# =========================================================

print()
print("=" * 70)
print("DECISION ENGINE INTEGRATION TEST PASSED")
print("=" * 70)