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

query = """
A new high-severity encoded PowerShell alert occurred on FIN-LT-014
using the a.rao account.

The PowerShell process was launched by winword.exe at approximately
14:17 during business hours.

What previous analyst experience is relevant to this alert?

Which conditions from previous experience do NOT match this alert?

Should the previous Likely Benign decision be directly applied to this alert?
"""

print("Running Hindsight mimic test...")
print(f"Bank: {bank_id}")
print()
print("New alert:")
print("ALT-003")
print("Encoded PowerShell")
print("Asset: FIN-LT-014")
print("Account: a.rao")
print("Parent process: winword.exe")
print("Time: 14:17")
print()
print("Recalled memories:")

response = client.recall(
    bank_id=bank_id,
    query=query,
)

if not response.results:
    print("No memories returned.")
else:
    for index, memory in enumerate(response.results, start=1):
        print()
        print(f"[Memory {index}]")
        print(f"Type: {memory.type}")
        print(f"Text: {memory.text}")

client.close()

print()
print("MIMIC TEST COMPLETE")