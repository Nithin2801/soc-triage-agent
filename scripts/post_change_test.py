from backend.app.tools import asset_lookup, user_lookup
from backend.app.memory import recall_experience
from backend.app.reasoner import (
    _build_memory_query,
    _build_reasoning_prompt,
    _filter_temporally_valid_memories,
    _get_groq_client,
    VERDICT_SCHEMA,
)

import json
import os


TEST_ALERT = {
    "alert_id": "POST-CHANGE-001",
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
print("POST-CHANGE ENVIRONMENT TEST")
print("=" * 70)

print()
print("TEST ALERT:")
print(json.dumps(TEST_ALERT, indent=2))

print()
print("Loading asset context...")

asset = asset_lookup(TEST_ALERT["asset_id"])

if asset is None:
    raise RuntimeError(
        f"Asset {TEST_ALERT['asset_id']} was not found."
    )

print(json.dumps(asset, indent=2))

print()
print("Loading account context...")

account = user_lookup(TEST_ALERT["account_id"])

if account is None:
    raise RuntimeError(
        f"Account {TEST_ALERT['account_id']} was not found."
    )

print(json.dumps(account, indent=2))

print()
print("Recalling Hindsight memories...")

memory_query = _build_memory_query(
    TEST_ALERT,
    asset,
    account,
)

recalled_memories = recall_experience(memory_query)

print()
print(f"Raw memories recalled: {len(recalled_memories)}")

print()
print("Applying temporal filtering...")

memories = _filter_temporally_valid_memories(
    TEST_ALERT,
    recalled_memories,
)

print(f"Temporally valid memories: {len(memories)}")

print()
print("TEMPORALLY VALID MEMORIES:")
print("-" * 70)

for index, memory in enumerate(memories, start=1):
    print(f"\nMemory {index}:")
    print(memory["text"])

print()
print("=" * 70)
print("ASKING GROQ FOR CANDIDATE DECISION")
print("=" * 70)

client = _get_groq_client()

model = os.getenv(
    "LLM_MODEL",
    "openai/gpt-oss-120b",
)

response = client.chat.completions.create(
    model=model,
    temperature=0,
    messages=[
        {
            "role": "system",
            "content": """
You are a SOC alert triage reasoning assistant.

Return only the requested structured recommendation.

Do not perform security actions.

Do not invent evidence.

Historical analyst feedback must not be treated
as current alert evidence unless the current alert
contains the relevant indicator.

Future events must not influence earlier alerts.

A newer environment change can supersede an older
benign exception when that change occurred before
or at the time of the current alert.
""",
        },
        {
            "role": "user",
            "content": _build_reasoning_prompt(
                TEST_ALERT,
                asset,
                account,
                memories,
            ),
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "soc_triage_verdict",
            "strict": True,
            "schema": VERDICT_SCHEMA,
        },
    },
)

content = response.choices[0].message.content

if not content:
    raise RuntimeError(
        "Groq returned an empty response."
    )

verdict = json.loads(content)

print()
print("=" * 70)
print("CANDIDATE DECISION")
print("=" * 70)

print(json.dumps(verdict, indent=2))

print()
print("=" * 70)
print("POST-CHANGE TEST COMPLETE")
print("=" * 70)