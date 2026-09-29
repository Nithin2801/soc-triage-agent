from datetime import datetime

from .memory import retain_experience


def record_analyst_feedback(
    alert,
    candidate_verdict,
    final_verdict,
    action,
    analyst_reason,
):
    """
    Store analyst approval or override as experiential memory.

    The stored memory includes:
    - alert identity
    - alert type
    - asset
    - account
    - important alert conditions
    - agent recommendation
    - final analyst decision
    - analyst reasoning
    """

    # =========================================================
    # VALIDATE ACTION
    # =========================================================

    action = action.lower().strip()

    if action not in ("approve", "override"):
        raise ValueError(
            "action must be 'approve' or 'override'."
        )

    # =========================================================
    # VALIDATE ANALYST REASON
    # =========================================================

    if not analyst_reason.strip():
        raise ValueError(
            "Analyst reason cannot be empty."
        )

    # =========================================================
    # EXTRACT ALERT INFORMATION
    # =========================================================

    alert_id = alert.get(
        "alert_id",
        "unknown",
    )

    alert_type = alert.get(
        "alert_type",
        "unknown",
    )

    asset_id = alert.get(
        "asset_id",
        "unknown",
    )

    account_id = alert.get(
        "account_id",
        "unknown",
    )

    timestamp = alert.get(
        "timestamp",
        "unknown",
    )

    parent_process = alert.get(
        "parent_process",
        "unknown",
    )

    process_name = alert.get(
        "process_name",
        "unknown",
    )

    command_line = alert.get(
        "command_line",
        "unknown",
    )

    # =========================================================
    # BUILD FEEDBACK DESCRIPTION
    # =========================================================

    if action == "approve":

        feedback_action = (
            "SOC analyst approved the agent "
            "recommendation."
        )

        decision_description = (
            f"The agent proposed "
            f"{candidate_verdict['verdict']} "
            f"and the final recommendation was "
            f"{final_verdict['verdict']}."
        )

        reason_label = "Analyst reason"

    else:

        feedback_action = (
            "SOC analyst overrode the agent "
            "recommendation."
        )

        decision_description = (
            f"The agent proposed "
            f"{candidate_verdict['verdict']} "
            f"but the analyst selected "
            f"{final_verdict['verdict']}."
        )

        reason_label = (
            "Analyst correction reason"
        )

    # =========================================================
    # BUILD RICH MEMORY CONTENT
    # =========================================================

    content = (
        f"{feedback_action} "
        f"Alert {alert_id}. "

        f"Alert type: {alert_type}. "

        f"Asset: {asset_id}. "

        f"Account: {account_id}. "

        f"Alert timestamp: {timestamp}. "

        f"Parent process: {parent_process}. "

        f"Process name: {process_name}. "

        f"Command line: {command_line}. "

        f"{decision_description} "

        f"{reason_label}: "
        f"{analyst_reason}"
    )

    # =========================================================
    # BUILD MEMORY CONTEXT
    # =========================================================

    context = (
        f"SOC analyst feedback for security alert "
        f"{alert_id}. "

        f"Alert type: {alert_type}. "

        f"Asset: {asset_id}. "

        f"Account: {account_id}. "

        f"Parent process: {parent_process}."
    )

    # =========================================================
    # FEEDBACK EVENT TIME
    # =========================================================

    feedback_timestamp = (
        datetime.now().isoformat()
    )

    # =========================================================
    # STORE IN HINDSIGHT
    # =========================================================

    retain_experience(
        content=content,
        context=context,
        timestamp=feedback_timestamp,
        document_id=(
            f"analyst-feedback-"
            f"{alert_id}-"
            f"{feedback_timestamp}"
        ),
    )

    # =========================================================
    # RETURN RESULT
    # =========================================================

    return {
        "success": True,
        "action": action,
        "alert_id": alert_id,
        "message": (
            "Analyst feedback retained "
            "in Hindsight."
        ),
    }