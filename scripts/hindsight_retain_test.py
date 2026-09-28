import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BASE_URL = os.environ["HINDSIGHT_BASE_URL"]
API_KEY = os.environ["HINDSIGHT_API_KEY"]
BANK_ID = os.environ["HINDSIGHT_BANK_ID"]


def main():
    print("Connecting to Hindsight...")

    client = Hindsight(
        base_url=BASE_URL,
        api_key=API_KEY,
    )

    print(f"Using bank: {BANK_ID}")

    client.retain(
        bank_id=BANK_ID,
        content=(
            "PERSISTENCE TEST: "
            "The SOC analyst confirmed that BKP-SRV-02 is a backup server "
            "using the svc-veeam account. "
            "Encoded PowerShell activity at 02:00 is expected only when "
            "the Veeam parent process and scheduled backup context match."
        ),
    )

    print("Persistence test memory retained successfully.")

    client.close()

    print("Hindsight client closed.")
    print("RETAIN process finished.")


if __name__ == "__main__":
    main()