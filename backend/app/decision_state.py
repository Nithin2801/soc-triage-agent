import json
from datetime import datetime

from .database import save_decision as save_decision_to_db
from .database import get_decision as get_decision_from_db


def save_decision(alert_id, decision):
    decision_json = json.dumps(decision)

    created_at = datetime.now().isoformat()

    save_decision_to_db(
        alert_id=alert_id,
        decision_json=decision_json,
        created_at=created_at,
    )


def get_decision(alert_id):
    decision_json = get_decision_from_db(alert_id)

    if decision_json is None:
        return None

    return json.loads(decision_json)


def clear_decisions():
    # Decision state is now persisted in SQLite.
    # This function is intentionally kept for compatibility.
    pass