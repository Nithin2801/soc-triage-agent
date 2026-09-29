import json
from datetime import datetime

from backend.app.database import (
    initialize_database,
    save_decision,
    get_decision,
)


initialize_database()

test_decision = {
    "alert_id": "TEST-001",
    "candidate_verdict": {
        "verdict": "Likely Benign",
        "confidence": 0.95,
    },
    "final_verdict": {
        "verdict": "Likely Benign",
        "confidence": 0.95,
    },
}

decision_json = json.dumps(test_decision)

created_at = datetime.now().isoformat()

save_decision(
    alert_id="TEST-001",
    decision_json=decision_json,
    created_at=created_at,
)

stored_json = get_decision("TEST-001")

assert stored_json is not None

stored_decision = json.loads(stored_json)

assert stored_decision["alert_id"] == "TEST-001"
assert stored_decision["candidate_verdict"]["verdict"] == "Likely Benign"
assert stored_decision["final_verdict"]["verdict"] == "Likely Benign"

print("STORED DECISION:")
print(stored_decision)

print()
print("SQLITE SAVE + GET TEST PASSED")