from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import Literal

from .data_loader import load_alerts
from .decision_engine import make_final_decision
from .feedback import record_analyst_feedback
from .decision_state import get_decision
from .database import initialize_database


app = FastAPI(
    title="SOC Alert Triage Agent",
    description="Security alert triage backend",
    version="0.1.0",
)
initialize_database()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_FILE = PROJECT_ROOT / "frontend" / "index.html"


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_FILE)

# =========================================================
# FEEDBACK REQUEST MODEL
# =========================================================

class FeedbackRequest(BaseModel):
    alert_id: str
    candidate_verdict: Literal[
        "Likely Benign",
        "Investigate",
        "Escalate",
    ]
    final_verdict: Literal[
        "Likely Benign",
        "Investigate",
        "Escalate",
    ]
    action: Literal["approve", "override"]
    analyst_reason: str


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "SOC Alert Triage Agent",
    }


# =========================================================
# GET ALL ALERTS
# =========================================================

@app.get("/alerts")
def get_alerts():
    return load_alerts()


# =========================================================
# GET ONE ALERT
# =========================================================

@app.get("/alerts/{alert_id}")
def get_alert(alert_id: str):

    alerts = load_alerts()

    for alert in alerts:

        if alert["alert_id"] == alert_id:
            return alert

    raise HTTPException(
        status_code=404,
        detail=f"Alert {alert_id} not found",
    )


# =========================================================
# TRIAGE ONE ALERT
# =========================================================

@app.post("/alerts/{alert_id}/triage")
def triage_alert(alert_id: str):

    try:

        return make_final_decision(
            alert_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Triage failed: {error}",
        )


# =========================================================
# RECORD ANALYST FEEDBACK
# =========================================================

@app.post("/feedback")
def submit_feedback(
    feedback: FeedbackRequest,
):

    # ---------------------------------------------------------
    # FIND ALERT
    # ---------------------------------------------------------

    alerts = load_alerts()

    alert = None

    for item in alerts:

        if item["alert_id"] == feedback.alert_id:

            alert = item
            break

    if alert is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Alert "
                f"{feedback.alert_id} "
                f"not found"
            ),
        )

    # ---------------------------------------------------------
    # VALIDATE ACTION
    # ---------------------------------------------------------

    action = feedback.action.lower().strip()

    if action not in (
        "approve",
        "override",
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "action must be "
                "'approve' or 'override'"
            ),
        )

    # ---------------------------------------------------------
    # VALIDATE ANALYST REASON
    # ---------------------------------------------------------

    if not feedback.analyst_reason.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Analyst reason cannot be empty."
            ),
        )

    # ---------------------------------------------------------
    # BUILD VERDICT OBJECTS
    # ---------------------------------------------------------

    stored_decision = get_decision(feedback.alert_id)

    if stored_decision is None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No stored triage decision found for "
                f"{feedback.alert_id}. "
                f"Run triage for this alert before submitting feedback."
            ),
        )

    candidate_verdict = stored_decision["candidate_verdict"]
    final_verdict = stored_decision["final_verdict"]

    # ---------------------------------------------------------
    # STORE FEEDBACK IN HINDSIGHT
    # ---------------------------------------------------------

    try:

        result = record_analyst_feedback(
            alert=alert,
            candidate_verdict=candidate_verdict,
            final_verdict=final_verdict,
            action=action,
            analyst_reason=(
                feedback.analyst_reason
            ),
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Feedback recording failed: "
                f"{error}"
            ),
        )