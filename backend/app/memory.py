import os

from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()


def _get_config():
    base_url = os.getenv("HINDSIGHT_BASE_URL")
    api_key = os.getenv("HINDSIGHT_API_KEY")
    bank_id = os.getenv("HINDSIGHT_BANK_ID")

    if not base_url:
        raise RuntimeError("HINDSIGHT_BASE_URL is missing from .env")

    if not api_key:
        raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

    if not bank_id:
        raise RuntimeError("HINDSIGHT_BANK_ID is missing from .env")

    return base_url, api_key, bank_id


def _create_client():
    base_url, api_key, _ = _get_config()

    return Hindsight(
        base_url=base_url,
        api_key=api_key,
    )


def recall_experience(query: str):
    """
    Retrieve relevant persistent SOC experience from Hindsight.
    """

    _, _, bank_id = _get_config()
    client = _create_client()

    try:
        response = client.recall(
            bank_id=bank_id,
            query=query,
        )

        memories = []

        for memory in response.results:
            memories.append(
                {
                    "type": memory.type,
                    "text": memory.text,
                }
            )

        return memories

    finally:
        client.close()


def retain_experience(
    content: str,
    context: str | None = None,
    timestamp: str | None = None,
    document_id: str | None = None,
):
    """
    Store analyst experience in Hindsight.
    """

    _, _, bank_id = _get_config()
    client = _create_client()

    try:
        kwargs = {
            "bank_id": bank_id,
            "content": content,
        }

        if context is not None:
            kwargs["context"] = context

        if timestamp is not None:
            kwargs["timestamp"] = timestamp

        if document_id is not None:
            kwargs["document_id"] = document_id

        return client.retain(**kwargs)

    finally:
        client.close()