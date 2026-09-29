from backend.app.data_loader import (
    load_accounts,
    load_alerts,
    load_assets,
    load_dataset_split,
    load_expected_decisions,
)


assets = load_assets()
accounts = load_accounts()
alerts = load_alerts()
expected_decisions = load_expected_decisions()
dataset_split = load_dataset_split()


print("DATA LOADER TEST")
print("----------------")

print(f"Assets loaded: {len(assets)}")
print(f"Accounts loaded: {len(accounts)}")
print(f"Alerts loaded: {len(alerts)}")
print(f"Expected decisions loaded: {len(expected_decisions)}")

print(
    f"Teaching cases: "
    f"{len(dataset_split['teaching_cases'])}"
)

print(
    f"Held-out cases: "
    f"{len(dataset_split['held_out_cases'])}"
)

print()
print("First asset:")
print(assets[0])

print()
print("First alert:")
print(alerts[0])

print()
print("DATA LOADER TEST PASSED")