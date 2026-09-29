from backend.app.reasoner import _select_relevant_memories


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


TEST_MEMORIES = [
    {
        "type": "world",
        "text": (
            "Security alert ALT-001 regarding Encoded PowerShell "
            "activity on asset BKP-SRV-01 was classified as Likely Benign. "
            "The activity was confirmed as expected Veeam backup operations "
            "during an approved window."
        ),
    },
    {
        "type": "world",
        "text": (
            "The 'Likely Benign' decision for ALT-001 is conditional and "
            "only applies when the backup-server role, svc-veeam account, "
            "Veeam parent process, and backup schedule match."
        ),
    },
    {
        "type": "world",
        "text": (
            "Security exception for encoded PowerShell activity associated "
            "with Veeam backup service is retired. "
            "When: 2026-09-29. "
            "The exception was only valid while the Veeam backup service "
            "was active."
        ),
    },
    {
        "type": "world",
        "text": (
            "Future encoded PowerShell activity must not be classified "
            "as Likely Benign based on historical Veeam backup patterns. "
            "The previous exception is superseded by the environment change."
        ),
    },
    {
        "type": "world",
        "text": (
            "BKP-SRV-02 is a backup server that uses the svc-veeam account."
        ),
    },
    {
        "type": "world",
        "text": (
            "The weather forecast for Hyderabad is sunny."
        ),
    },
]


print("=" * 70)
print("MEMORY EVIDENCE SELECTION TEST")
print("=" * 70)

print()
print(f"Input memories: {len(TEST_MEMORIES)}")

selected_memories = _select_relevant_memories(
    TEST_ALERT,
    TEST_MEMORIES,
)

print(
    f"Selected memories: "
    f"{len(selected_memories)}"
)

print()
print("SELECTED MEMORIES")
print("-" * 70)

for index, memory in enumerate(
    selected_memories,
    start=1,
):
    print()
    print(f"Memory {index}:")
    print(memory["text"])


selected_text = [
    memory["text"]
    for memory in selected_memories
]

print()
print("=" * 70)
print("ASSERTIONS")
print("=" * 70)

assert selected_memories, (
    "No relevant memories were selected."
)

assert any(
    "BKP-SRV-02" in text
    for text in selected_text
), "Relevant BKP-SRV-02 memory was not selected."

assert any(
    "svc-veeam" in text
    for text in selected_text
), "Relevant svc-veeam memory was not selected."

assert any(
    "Veeam" in text
    for text in selected_text
), "Relevant Veeam memory was not selected."

assert any(
    "retired" in text.lower()
    or "superseded" in text.lower()
    or "decommissioned" in text.lower()
    for text in selected_text
), "Environment-change evidence was not selected."

assert not any(
    "weather forecast" in text.lower()
    for text in selected_text
), "Irrelevant memory was incorrectly selected."

print()
print("ALL MEMORY EVIDENCE SELECTION ASSERTIONS PASSED")

print()
print("=" * 70)
print("MEMORY EVIDENCE SELECTION TEST PASSED")
print("=" * 70)