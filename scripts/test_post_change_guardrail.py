from backend.app.tools import asset_lookup, user_lookup
from backend.app.memory import recall_experience
from backend.app.reasoner import _build_memory_query
from backend.app.guardrails import apply_benign_memory_guardrail

import json


TEST_ALERT = {
    "alert_id": "POST-CHANGE-GUARDRAIL-001",
    "alert_type": "Encoded PowerShell",
    "technique_id": "T1059.001",
    "severity": "medium",
    "asset_id": "BKP-SRV-02",
    "account_id": "svc-veeam",
    "timestamp": "2026-09-29T02:05:00",
    "parent_process": "Veeam.Backup.Service.exe",
    "command_pattern": "Encoded PowerShell command",
    "source_ip": "10.10.20.12",
    "description": (
        "Encoded PowerShell launched by the Veeam backup service "
        "during the scheduled backup window."
    ),
}


print("=" * 70)
print("POST-CHANGE GUARDRAIL TEST")
print("=" * 70)

asset = asset_lookup(TEST_ALERT["asset_id"])
account = user_lookup(TEST_ALERT["account_id"])

if asset is None:
    raise RuntimeError("Test asset was not found.")

if account is None:
    raise RuntimeError("Test account was not found.")

print()
print("Test alert:")
print(json.dumps(TEST_ALERT, indent=2))

print()
print("Recalling Hindsight memories...")

memory_query = _build_memory_query(
    TEST_ALERT,
    asset,
    account,
)

memories = recall_experience(memory_query)

print(f"Memories recalled: {len(memories)}")

print()
print("Searching for environment-change evidence...")

for index, memory in enumerate(memories, start=1):
    text = memory.get("text", "")

    if (
        "decommissioned" in text.lower()
        or "exception retired" in text.lower()
        or "previous exception is superseded" in text.lower()
        or "no longer authorized" in text.lower()
    ):
        print()
        print(f"Change memory {index}:")
        print(text)


print()
print("=" * 70)
print("SIMULATING AN INCORRECT GROQ DECISION")
print("=" * 70)

candidate_verdict = {
    "verdict": "Likely Benign",
    "confidence": 0.99,
    "reasoning": (
        "Simulated incorrect LLM recommendation: "
        "the historical Veeam benign conditions match."
    ),
    "matched_conditions": [
        "asset role matches backup_server",
        "account matches svc-veeam",
        "parent process matches Veeam.Backup.Service.exe",
        "timestamp matches approved backup hour (02:00)",
    ],
    "mismatched_conditions": [],
    "memory_evidence": [],
}


print()
print("BEFORE GUARDRAIL:")
print(json.dumps(candidate_verdict, indent=2))

print()
print("Applying independent Python guardrail...")

final_verdict = apply_benign_memory_guardrail(
    TEST_ALERT,
    asset,
    account,
    memories,
    candidate_verdict,
)

print()
print("=" * 70)
print("AFTER GUARDRAIL")
print("=" * 70)

print(json.dumps(final_verdict, indent=2))

print()
print("=" * 70)

if final_verdict["verdict"] == "Investigate":
    print("POST-CHANGE GUARDRAIL TEST PASSED")
    print()
    print(
        "The guardrail prevented a Likely Benign recommendation "
        "after the Veeam exception had been superseded."
    )
else:
    print("POST-CHANGE GUARDRAIL TEST FAILED")
    print(
        f"Expected Investigate, got {final_verdict['verdict']}"
    )

print("=" * 70)