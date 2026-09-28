import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BASE_URL = os.environ["HINDSIGHT_BASE_URL"]
API_KEY = os.environ["HINDSIGHT_API_KEY"]
BANK_ID = os.environ["HINDSIGHT_BANK_ID"]


def main():
    print("Starting a new Hindsight recall process...")
    print(f"Using bank: {BANK_ID}")

    client = Hindsight(
        base_url=BASE_URL,
        api_key=API_KEY,
    )

    result = client.recall(
        bank_id=BANK_ID,
        query=(
            "What did the SOC analyst learn about "
            "BKP-SRV-02, the svc-veeam account, "
            "and encoded PowerShell at 02:00?"
        ),
    )

    print("\nRecalled memories:")

    if not result.results:
        print("NO MEMORIES FOUND")
    else:
        for memory in result.results:
            print("- " + memory.text)

    client.close()

    print("\nRECALL process finished.")


if __name__ == "__main__":
    main()