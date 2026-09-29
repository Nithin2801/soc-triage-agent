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
A new medium-severity encoded PowerShell alert occurred on BKP-SRV-02
using the svc-veeam account. The process was launched by
Veeam.Backup.Service.exe at approximately 02:05 during the scheduled
backup window.

What previous analyst experience is relevant to this alert?
What conditions were required for the previous Likely Benign decision?
"""

print("Recalling Hindsight experience...")
print(f"Bank: {bank_id}")
print()
print("Query:")
print(query.strip())
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
print("HINDSIGHT TRANSFER RECALL TEST COMPLETE")