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


memory = """
SOC analyst case note for alert ALT-001.

The analyst reviewed an encoded PowerShell alert on BKP-SRV-01.

The alert involved the svc-veeam service account.
The PowerShell process was launched by Veeam.Backup.Service.exe.
The activity occurred at approximately 02:00 during the approved backup window.
BKP-SRV-01 is an approved production backup server.

The analyst confirmed this combination of conditions as expected Veeam backup behavior.

Analyst decision: Likely Benign.

Important condition: this decision applies only when the relevant backup-server role,
svc-veeam account, Veeam parent process, and approved backup schedule all match.

If these conditions do not match, the previous decision must not automatically be applied.
"""

print("Teaching Hindsight with ALT-001...")
print(f"Bank: {bank_id}")

client.retain(
    bank_id=bank_id,
    content=memory,
    context="SOC analyst confirmed security alert disposition",
    document_id="soc-case-ALT-001",
    metadata={
        "alert_id": "ALT-001",
        "decision": "Likely Benign",
        "source": "synthetic analyst teaching case",
    },
)

print()
print("ALT-001 retained successfully.")
print("Hindsight teaching case complete.")

client.close()