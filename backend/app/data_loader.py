import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def load_json(filename: str):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_assets():
    return load_json("assets.json")


def load_accounts():
    return load_json("accounts.json")


def load_alerts():
    return load_json("alerts.json")


def load_expected_decisions():
    return load_json("expected_decisions.json")


def load_dataset_split():
    return load_json("dataset_split.json")