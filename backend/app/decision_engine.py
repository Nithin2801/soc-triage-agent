from .reasoner import analyze_alert
from .decision_state import save_decision
from .guardrails import (
    apply_critical_severity_guardrail,
    apply_critical_asset_guardrail,
    apply_benign_memory_guardrail,
)


def make_final_decision(alert_id: str):
    """
    Run the complete SOC triage decision pipeline.

    Pipeline:

        Alert
          ↓
        Current context
          ↓
        Hindsight recall
          ↓
        Groq reasoning
          ↓
        Critical severity guardrail
          ↓
        Critical asset guardrail
          ↓
        Conditional Hindsight-memory guardrail
          ↓
        Final recommendation
    """

    # ---------------------------------------------------------
    # STEP 1 — Run Hindsight + Groq reasoning
    # ---------------------------------------------------------

    analysis = analyze_alert(alert_id)

    alert = analysis["alert"]
    asset = analysis["asset"]
    account = analysis["account"]
    memories = analysis["memories"]

    candidate_verdict = analysis["candidate_verdict"]

    # ---------------------------------------------------------
    # STEP 2 — Critical severity guardrail
    # ---------------------------------------------------------

    candidate_verdict = apply_critical_severity_guardrail(
        alert,
        candidate_verdict,
    )

    # ---------------------------------------------------------
    # STEP 3 — Critical asset guardrail
    # ---------------------------------------------------------

    candidate_verdict = apply_critical_asset_guardrail(
        alert,
        asset,
        candidate_verdict,
    )

    # ---------------------------------------------------------
    # STEP 4 — Conditional Hindsight-memory guardrail
    # ---------------------------------------------------------

    candidate_verdict = apply_benign_memory_guardrail(
        alert,
        asset,
        account,
        memories,
        candidate_verdict,
    )

    # ---------------------------------------------------------
    # STEP 5 — Build final result
    # ---------------------------------------------------------

    result = {
        "alert": alert,
        "asset": asset,
        "account": account,
        "memories": memories,
        "candidate_verdict": analysis["candidate_verdict"],
        "final_verdict": candidate_verdict,
    }

    save_decision(alert_id, result)

    return result