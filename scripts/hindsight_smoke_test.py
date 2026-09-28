import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()


BASE_URL = os.environ["HINDSIGHT_BASE_URL"]
API_KEY = os.environ["HINDSIGHT_API_KEY"]
BANK_ID = os.environ["HINDSIGHT_BANK_ID"]


def main():
    print("Connecting to Hindsight...")
    print(f"Base URL: {BASE_URL}")
    print(f"Bank ID: {BANK_ID}")

    client = Hindsight(
        base_url=BASE_URL,
        api_key=API_KEY,
    )

    print("Hindsight client created successfully.")

    bank = client.create_bank(
        bank_id=BANK_ID,
        name="SOC Alert Triage Development",
    )

    print(f"Bank ready: {bank.bank_id}")

    client.retain(
        bank_id=BANK_ID,
        content=(
            "Synthetic SOC training case: "
            "BKP-SRV-01 is a backup server using the svc-veeam account. "
            "Encoded PowerShell launched by the Veeam backup process at 02:00 "
            "was reviewed by the analyst and confirmed as expected backup behavior. "
            "The analyst classified this pattern as Likely Benign when the "
            "backup-server role, svc-veeam account, Veeam parent process, "
            "and scheduled backup window all match."
        ),
    )

    print("Memory retained successfully.")

    result = client.recall(
        bank_id=BANK_ID,
        query=(
            "What did the analyst learn about encoded PowerShell "
            "activity on the Veeam backup server?"
        ),
    )

    print("\nRecalled memories:")

    for memory in result.results:
        print("- " + memory.text)

    client.close()

    print("\nHINDSIGHT SMOKE TEST PASSED")


if __name__ == "__main__":
    main()