from backend.app.guardrails import (
    check_benign_memory_conditions,
)
from backend.app.tools import (
    alert_context,
    asset_lookup,
    user_lookup,
)


def test_alert(alert_id):
    alert = alert_context(alert_id)

    if alert is None:
        raise ValueError(f"Alert {alert_id} not found")

    asset = asset_lookup(alert["asset_id"])

    if asset is None:
        raise ValueError(
            f"Asset {alert['asset_id']} not found"
        )

    account = user_lookup(alert["account_id"])

    if account is None:
        raise ValueError(
            f"Account {alert['account_id']} not found"
        )

    candidate_verdict = {
        "verdict": "Likely Benign",
        "confidence": 0.90,
    }

    result = check_benign_memory_conditions(
        alert,
        asset,
        account,
        candidate_verdict,
    )

    print()
    print("=" * 60)
    print(f"TESTING {alert_id}")
    print("=" * 60)

    print()
    print("Alert:")
    print(f"  Asset: {alert['asset_id']}")
    print(f"  Account: {alert['account_id']}")
    print(f"  Parent: {alert['parent_process']}")

    print()
    print("Condition check:")
    print(result)

    return result


# ---------------------------------------------------------
# TEST 1: Known matching benign scenario
# ---------------------------------------------------------

result_001 = test_alert("ALT-001")

assert result_001["conditions_match"] is True

assert len(result_001["matched_conditions"]) == 4


# ---------------------------------------------------------
# TEST 2: Similar alert, but conditions do not match
# ---------------------------------------------------------

result_003 = test_alert("ALT-003")

assert result_003["conditions_match"] is False

assert len(result_003["matched_conditions"]) < 3


print()
print("=" * 60)
print("BENIGN MEMORY CONDITION TEST PASSED")
print("=" * 60)