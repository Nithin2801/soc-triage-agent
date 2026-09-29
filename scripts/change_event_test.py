import os

from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()

base_url = os.getenv("HINDSIGHT_BASE_URL")
api_key = os.getenv("HINDSIGHT_API_KEY")
bank_id = os.getenv("HINDSIGHT_BANK_ID")

if not base_url:
    raise RuntimeError("HINDSIGHT_BASE_URL is missing from .env")

if not api_key:
    raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

if not bank_id:
    raise RuntimeError("HINDSIGHT_BANK_ID is missing from .env")


client = Hindsight(
    base_url=base_url,
    api_key=api_key,
)


change_event = """
SOC environment change event.

Effective date: 2026-09-29.

The Veeam backup service has been decommissioned from the environment.
The approved Veeam backup process Veeam.Backup.Service.exe is no longer
an authorized source of PowerShell activity on BKP-SRV-01, BKP-SRV-02,
or BKP-SRV-03.

The previous analyst exception for encoded PowerShell activity was valid
only while the Veeam backup service was active.

This is a newer environment change and therefore supersedes the previous
Veeam-specific benign exception for future alerts.

Future encoded PowerShell activity must not be classified as Likely Benign
solely because it resembles the historical Veeam backup pattern.
"""

print("Recording environment change event...")
print(f"Bank: {bank_id}")
print()
print(change_event.strip())
print()

client.retain(
    bank_id=bank_id,
    content=change_event,
    context="SOC environment change and retirement of an approved security exception",
    timestamp="2026-09-29T00:00:00",
    document_id="soc-change-2026-09-29-veeam-decommission",
    metadata={
        "event_type": "environment_change",
        "effective_date": "2026-09-29",
        "affected_service": "Veeam.Backup.Service.exe",
        "affected_assets": "BKP-SRV-01, BKP-SRV-02, BKP-SRV-03"
    },
)

client.close()

print("Environment change event retained successfully.")
print("CHANGE EVENT TEST COMPLETE")