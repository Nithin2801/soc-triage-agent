from backend.app.tools import (
    alert_context,
    asset_lookup,
    user_lookup,
)


print("SECURITY CONTEXT TOOLS TEST")
print("---------------------------")


alert = alert_context("ALT-001")

if alert is None:
    raise RuntimeError("ALT-001 was not found")

print()
print("1. ALERT CONTEXT")
print(alert)


asset = asset_lookup(alert["asset_id"])

if asset is None:
    raise RuntimeError(
        f"Asset {alert['asset_id']} was not found"
    )

print()
print("2. ASSET LOOKUP")
print(asset)


account = user_lookup(alert["account_id"])

if account is None:
    raise RuntimeError(
        f"Account {alert['account_id']} was not found"
    )

print()
print("3. ACCOUNT LOOKUP")
print(account)


print()
print("SECURITY CONTEXT TOOLS TEST PASSED")