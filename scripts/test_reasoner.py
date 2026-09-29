import json

from backend.app.reasoner import analyze_alert


TEST_ALERTS = [
    "ALT-001",
    "ALT-003",
    "ALT-004",
]


for alert_id in TEST_ALERTS:
    print()
    print("=" * 70)
    print(f"TESTING {alert_id}")
    print("=" * 70)

    result = analyze_alert(alert_id)

    alert = result["alert"]
    candidate = result["candidate_verdict"]

    print()
    print("ALERT:")
    print(
        f"  ID: {alert['alert_id']}"
    )
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
        f"HINDSIGHT MEMORIES: "
        f"{len(result['memories'])}"
    )

    print()
    print("GROQ CANDIDATE:")
    print(
        json.dumps(
            candidate,
            indent=2,
        )
    )

    print()
    print(
        f"FINAL CANDIDATE VERDICT: "
        f"{candidate['verdict']}"
    )

print()
print("=" * 70)
print("REASONER MULTI-ALERT TEST PASSED")
print("=" * 70)