def apply_critical_severity_guardrail(alert, candidate_verdict):
    """
    Prevent critical-severity alerts from being classified
    as Likely Benign.
    """

    verdict = candidate_verdict["verdict"]

    if (
        alert["severity"].lower() == "critical"
        and verdict == "Likely Benign"
    ):
        candidate_verdict["verdict"] = "Escalate"

        candidate_verdict["reasoning"] += (
            " Guardrail override: critical-severity alerts "
            "cannot be classified as Likely Benign."
        )

        candidate_verdict["guardrail_override"] = True
        candidate_verdict["guardrail_reason"] = (
            "Critical severity prevents a Likely Benign recommendation."
        )

    else:
        candidate_verdict["guardrail_override"] = False
        candidate_verdict["guardrail_reason"] = None

    return candidate_verdict

def apply_critical_asset_guardrail(alert, asset, candidate_verdict):
    """
    Prevent critical assets from being classified
    as Likely Benign.
    """

    verdict = candidate_verdict["verdict"]

    if (
        asset["criticality"].lower() == "critical"
        and verdict == "Likely Benign"
    ):
        candidate_verdict["verdict"] = "Escalate"

        candidate_verdict["reasoning"] += (
            " Guardrail override: critical assets "
            "cannot be classified as Likely Benign."
        )

        candidate_verdict["guardrail_override"] = True
        candidate_verdict["guardrail_reason"] = (
            "Critical asset prevents a Likely Benign recommendation."
        )

    return candidate_verdict

def check_benign_memory_conditions(alert, asset, account, candidate_verdict):
    """
    Check whether the candidate Likely Benign decision has
    evidence that the important historical conditions match
    the current alert.
    """

    if candidate_verdict["verdict"] != "Likely Benign":
        return {
            "conditions_match": False,
            "reason": "Candidate verdict is not Likely Benign.",
            "matched_conditions": [],
        }

    required_conditions = {
        "asset_role": "backup_server",
        "account_id": "svc-veeam",
        "parent_process": "Veeam.Backup.Service.exe",
        "backup_hour":2,
    }

    matched_conditions = []

    if asset.get("role") == required_conditions["asset_role"]:
        matched_conditions.append(
            "asset role matches backup_server"
        )

    if account.get("account_id") == required_conditions["account_id"]:
        matched_conditions.append(
            "account matches svc-veeam"
        )

    if alert.get("parent_process") == required_conditions["parent_process"]:
        matched_conditions.append(
            "parent process matches Veeam.Backup.Service.exe"
        )

    timestamp = alert.get("timestamp", "")

    if "T" in timestamp:
        alert_hour = int(
            timestamp.split("T")[1].split(":")[0]
        )

        if alert_hour == required_conditions["backup_hour"]:
            matched_conditions.append(
                "timestamp matches approved backup hour (02:00)"
            )

    all_required_conditions_match = (
        len(matched_conditions) == len(required_conditions)
    )

    if all_required_conditions_match:
        return {
            "conditions_match": True,
            "reason": "All required historical benign conditions match.",
            "matched_conditions": matched_conditions,
        }

    return {
        "conditions_match": False,
        "reason": (
            "One or more required historical benign "
            "conditions do not match."
        ),
        "matched_conditions": matched_conditions,
    }

def check_newer_memory_conflict(alert, memories):
    """
    Check whether a newer Hindsight memory indicates that
    the historical benign exception has been retired or
    superseded.
    """

    alert_timestamp = alert.get("timestamp", "")

    if not alert_timestamp:
        return {
            "conflict": False,
            "reason": "Alert timestamp is unavailable.",
        }

    conflict_phrases = [
        "decommissioned",
        "exception retired",
        "exception is retired",
        "previous exception is superseded",
        "no longer authorized",
        "classification retired",
    ]

    for memory in memories:
        memory_text = memory.get("text", "")

        normalized_text = memory_text.lower()

        has_conflict_phrase = any(
            phrase in normalized_text
            for phrase in conflict_phrases
        )

        if not has_conflict_phrase:
            continue

        # Look for a YYYY-MM-DD date in the memory.
        import re

        dates = re.findall(
            r"\b\d{4}-\d{2}-\d{2}\b",
            memory_text,
        )

        for date_value in dates:
            change_timestamp = f"{date_value}T00:00:00"

            if change_timestamp > alert_timestamp:
                return {
                    "conflict": True,
                    "reason": (
                        "A newer Hindsight memory indicates that "
                        "the historical benign exception was "
                        "retired or superseded."
                    ),
                    "effective_date": date_value,
                    "memory": memory_text,
                }

    return {
        "conflict": False,
        "reason": (
            "No newer memory was found that retires or "
            "supersedes the historical benign exception."
        ),
    }

def check_effective_memory_change(alert, memories):
    """
    Determine whether a relevant environment change was already
    effective when the alert occurred.
    """

    alert_timestamp = alert.get("timestamp", "")

    if not alert_timestamp:
        return {
            "effective_change": False,
            "reason": "Alert timestamp is unavailable.",
        }

    import re

    change_phrases = [
        "decommissioned",
        "exception retired",
        "exception is retired",
        "previous exception is superseded",
        "no longer authorized",
        "classification retired",
    ]

    for memory in memories:
        memory_text = memory.get("text", "")
        normalized_text = memory_text.lower()

        has_change_phrase = any(
            phrase in normalized_text
            for phrase in change_phrases
        )

        if not has_change_phrase:
            continue

        dates = re.findall(
            r"\b\d{4}-\d{2}-\d{2}\b",
            memory_text,
        )

        for date_value in dates:
            change_timestamp = f"{date_value}T00:00:00"

            if change_timestamp <= alert_timestamp:
                return {
                    "effective_change": True,
                    "reason": (
                        "A relevant environment change was "
                        "already effective when this alert occurred."
                    ),
                    "effective_date": date_value,
                    "memory": memory_text,
                }

    return {
        "effective_change": False,
        "reason": (
            "No relevant environment change was already "
            "effective when this alert occurred."
        ),
    }

def apply_benign_memory_guardrail(
    alert,
    asset,
    account,
    memories,
    candidate_verdict,
):
    """
    Allow Likely Benign only when:
    1. The Groq candidate is Likely Benign.
    2. Required historical conditions match.
    3. No relevant environment change was already effective.
    """

    # ---------------------------------------------------------
    # If Groq did not recommend Likely Benign,
    # this guardrail does not change the verdict.
    # ---------------------------------------------------------

    if candidate_verdict["verdict"] != "Likely Benign":
        return candidate_verdict

    # ---------------------------------------------------------
    # Check historical conditions
    # ---------------------------------------------------------

    condition_result = check_benign_memory_conditions(
        alert,
        asset,
        account,
        candidate_verdict,
    )

    # ---------------------------------------------------------
    # If required conditions do not match,
    # prevent Likely Benign.
    # ---------------------------------------------------------

    if not condition_result["conditions_match"]:
        candidate_verdict["verdict"] = "Investigate"

        candidate_verdict["reasoning"] += (
            " Guardrail override: the current alert does not "
            "match all required conditions of the historical "
            "benign exception."
        )

        candidate_verdict["guardrail_override"] = True

        candidate_verdict["guardrail_reason"] = (
            "Historical benign conditions do not match."
        )

        return candidate_verdict

    # ---------------------------------------------------------
    # Check whether a relevant environment change
    # was already effective.
    # ---------------------------------------------------------

    change_result = check_effective_memory_change(
        alert,
        memories,
    )

    # ---------------------------------------------------------
    # If the old exception was already retired,
    # prevent Likely Benign.
    # ---------------------------------------------------------

    if change_result["effective_change"]:
        candidate_verdict["verdict"] = "Investigate"

        candidate_verdict["reasoning"] += (
            " Guardrail override: a newer environment change "
            "was already effective when this alert occurred, "
            "so the historical benign exception cannot be used."
        )

        candidate_verdict["guardrail_override"] = True

        candidate_verdict["guardrail_reason"] = (
            "Historical benign exception was already "
            "superseded by an effective environment change."
        )

        return candidate_verdict

    # ---------------------------------------------------------
    # All benign-memory checks passed.
    # ---------------------------------------------------------

    candidate_verdict["guardrail_override"] = False

    candidate_verdict["guardrail_reason"] = (
        "Historical benign conditions match and no effective "
        "environment change invalidates the exception."
    )

    return candidate_verdict