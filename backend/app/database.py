import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "soc_triage.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS triage_decisions (
                alert_id TEXT PRIMARY KEY,
                decision_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()

def save_decision(alert_id, decision_json, created_at):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR REPLACE INTO triage_decisions
            (alert_id, decision_json, created_at)
            VALUES (?, ?, ?)
            """,
            (alert_id, decision_json, created_at),
        )

        connection.commit()

    finally:
        connection.close()
        
def get_decision(alert_id):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT decision_json
            FROM triage_decisions
            WHERE alert_id = ?
            """,
            (alert_id,),
        ).fetchone()

        if row is None:
            return None

        return row["decision_json"]

    finally:
        connection.close()