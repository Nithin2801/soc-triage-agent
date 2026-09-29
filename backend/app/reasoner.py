import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq

from .memory import recall_experience
from .tools import (
    alert_context,
    asset_lookup,
    user_lookup,
)


load_dotenv()


VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": [
                "Likely Benign",
                "Investigate",
                "Escalate",
            ],
        },
        "confidence": {
            "type": "number",
        },
        "reasoning": {
            "type": "string",
        },
        "matched_conditions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "mismatched_conditions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "memory_evidence": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "verdict",
        "confidence",
        "reasoning",
        "matched_conditions",
        "mismatched_conditions",
        "memory_evidence",
    ],
    "additionalProperties": False,
}


def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing from .env"
        )

    return Groq(api_key=api_key)


def _extract_memory_dates(memory_text):
    """
    Extract ISO dates such as 2026-09-29
    from Hindsight memory text.
    """

    return re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b",
        memory_text,
    )


def _filter_temporally_valid_memories(
    alert,
    memories,
):
    """
    Remove memories that describe events occurring
    after the current alert.

    Example:

        Alert: 2026-09-28

        Memory: 2026-09-29 decommission

    The 2026-09-29 memory cannot influence
    the 2026-09-28 decision.
    """

    alert_timestamp = alert.get("timestamp")

    if not alert_timestamp:
        return memories

    alert_datetime = datetime.fromisoformat(
        alert_timestamp
    )

    valid_memories = []

    for memory in memories:

        memory_text = memory.get(
            "text",
            "",
        )

        dates = _extract_memory_dates(
            memory_text
        )



        # -----------------------------------------------------
        # Undated environment-change memories are unsafe for
        # historical reasoning because their effective date
        # cannot be established.
        # -----------------------------------------------------

        normalized_memory = memory_text.lower()

        environment_change_terms = [
            "decommissioned",
            "decommissioned from the environment",
            "superseded",
            "exception is retired",
            "exception was retired",
            "no longer authorized",
            "environment change",
        ]

        is_environment_change = any(
            term in normalized_memory
            for term in environment_change_terms
        )

        if is_environment_change and not dates:
            continue

        future_memory = False

        for date_text in dates:

            memory_date = datetime.fromisoformat(
                date_text
            ).date()

            if memory_date > alert_datetime.date():
                future_memory = True
                break

        if not future_memory:
            valid_memories.append(memory)

    return valid_memories

def _select_relevant_memories(
    alert,
    memories,
    max_memories=6,
):
    """
    Select the most relevant Hindsight memories for the
    current alert.

    This does not delete memories from Hindsight.

    It only controls which recalled memories are presented
    as evidence to the reasoning layer.
    """

    if not memories:
        return []

    alert_text = " ".join(
        [
            str(alert.get("alert_id", "")),
            str(alert.get("alert_type", "")),
            str(alert.get("technique_id", "")),
            str(alert.get("asset_id", "")),
            str(alert.get("account_id", "")),
            str(alert.get("parent_process", "")),
            str(alert.get("command_pattern", "")),
            str(alert.get("description", "")),
        ]
    ).lower()

    asset_id = str(
        alert.get("asset_id", "")
    ).lower()

    account_id = str(
        alert.get("account_id", "")
    ).lower()

    parent_process = str(
        alert.get("parent_process", "")
    ).lower()

    alert_type = str(
        alert.get("alert_type", "")
    ).lower()

    scored_memories = []

    for memory in memories:
        text = str(
            memory.get("text", "")
        )

        normalized_text = text.lower()

        score = 0

        # -----------------------------------------------------
        # Current asset relevance
        # -----------------------------------------------------

        if asset_id and asset_id in normalized_text:
            score += 5

        # -----------------------------------------------------
        # Current account relevance
        # -----------------------------------------------------

        if account_id and account_id in normalized_text:
            score += 5

        # -----------------------------------------------------
        # Current parent-process relevance
        # -----------------------------------------------------

        if (
            parent_process
            and parent_process in normalized_text
        ):
            score += 5

        # -----------------------------------------------------
        # Alert-type relevance
        # -----------------------------------------------------

        if (
            alert_type
            and alert_type in normalized_text
        ):
            score += 3

        # -----------------------------------------------------
        # Important security context
        # -----------------------------------------------------

        security_terms = [
            "likely benign",
            "investigate",
            "escalate",
            "exception",
            "decommissioned",
            "retired",
            "superseded",
            "no longer authorized",
            "environment change",
            "backup",
            "scheduled",
        ]

        for term in security_terms:
            if term in normalized_text:
                score += 1

        # -----------------------------------------------------
        # Technique / command relevance
        # -----------------------------------------------------

        technique_id = str(
            alert.get("technique_id", "")
        ).lower()

        command_pattern = str(
            alert.get("command_pattern", "")
        ).lower()

        if (
            technique_id
            and technique_id in normalized_text
        ):
            score += 2

        if (
            command_pattern
            and command_pattern.lower()
            in normalized_text
        ):
            score += 2

        # -----------------------------------------------------
        # Keep the memory and its score together.
        # -----------------------------------------------------

        scored_memories.append(
            (
                score,
                memory,
            )
        )

    # ---------------------------------------------------------
    # Highest relevance first.
    # ---------------------------------------------------------

    scored_memories.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    selected = []

    for score, memory in scored_memories:

        # Ignore memories with no meaningful relationship
        # to the current alert.
        if score <= 0:
            continue

        selected.append(memory)

        if len(selected) >= max_memories:
            break

    return selected

def _build_memory_query(alert, asset, account):
    return f"""
SOC alert triage context.

Alert:
{json.dumps(alert, indent=2)}

Asset:
{json.dumps(asset, indent=2)}

Account:
{json.dumps(account, indent=2)}

Retrieve previous analyst experience that is relevant
to this alert.

Pay particular attention to:

- previous analyst verdicts
- conditions required for those verdicts
- asset roles
- account identity
- parent processes
- schedules
- environment changes
- newer information that may supersede older exceptions

TEMPORAL RULE:

Only memories that were valid on or before the
current alert date should influence the decision.

Do not use future events to explain an earlier alert.

Do not assume a previous verdict applies merely because
the alert type is similar.
"""


def _build_reasoning_prompt(
    alert,
    asset,
    account,
    memories,
):
    return f"""
You are the reasoning layer of a SOC alert triage agent.

Your task is to produce a recommendation for a human
SOC analyst.

IMPORTANT RULES:

1. You are recommending an action, not taking an action.

2. Never claim that the alert was automatically closed,
   blocked, isolated, or remediated.

3. A historical Likely Benign decision is conditional.

4. Do not apply a historical benign decision merely because
   the alert type looks similar.

5. Compare the current alert conditions with the conditions
   recorded in historical memory.

6. ONLY use historical memories that could have been known
   at the time of the current alert.

7. A memory describing an event after the current alert
   timestamp MUST NOT influence the current decision.

8. A historical analyst override or correction is evidence
   about a previous analyst decision. It is NOT proof that
   the same suspicious indicator exists in the current alert.

9. If a historical memory says an analyst observed an
   additional suspicious indicator, but that indicator is
   absent from the current alert, do NOT claim that the
   indicator is present now.

10. Current alert evidence has priority over assumptions
    derived from historical feedback.

11. Newer environment-change memories can supersede older
    exceptions, but only when the change occurred before
    or at the time of the current alert.

12. If important current conditions conflict or are missing,
    prefer Investigate or Escalate.

13. Treat Hindsight memories as evidence, not unquestionable
    truth.

14. Do not invent facts that are absent from the current alert,
    current asset/account context, or recalled memories.

15. The final system will apply independent code guardrails
    after your recommendation.

CURRENT ALERT:

{json.dumps(alert, indent=2)}

CURRENT ASSET:

{json.dumps(asset, indent=2)}

CURRENT ACCOUNT:

{json.dumps(account, indent=2)}

TEMPORALLY VALID HINDSIGHT MEMORIES:

{json.dumps(memories, indent=2)}

IMPORTANT CURRENT-EVIDENCE CHECK:

Before using a historical analyst correction as a reason
to recommend Investigate, verify that the suspicious
indicator described by that correction is actually present
in the CURRENT ALERT.

If it is not present, do not treat that historical
indicator as current evidence.

Return your candidate SOC recommendation.
"""


def analyze_alert(alert_id: str, memory_enabled: bool = True):

    # =========================================================
    # STEP 1 — LOAD CURRENT ALERT
    # =========================================================

    alert = alert_context(alert_id)

    if alert is None:
        raise ValueError(
            f"Alert {alert_id} was not found"
        )

    # =========================================================
    # STEP 2 — LOAD CURRENT ASSET
    # =========================================================

    asset = asset_lookup(
        alert["asset_id"]
    )

    if asset is None:
        raise ValueError(
            f"Asset {alert['asset_id']} was not found"
        )

    # =========================================================
    # STEP 3 — LOAD CURRENT ACCOUNT
    # =========================================================

    account = user_lookup(
        alert["account_id"]
    )

    if account is None:
        raise ValueError(
            f"Account {alert['account_id']} was not found"
        )

        # =========================================================
    # STEP 4 — HINDSIGHT MEMORY
    # =========================================================

    if memory_enabled:

        # Build the Hindsight query only when memory is ON.
        memory_query = _build_memory_query(
            alert,
            asset,
            account,
        )

        # Recall previous analyst experience.
        recalled_memories = recall_experience(
            memory_query
        )

        # =====================================================
        # STEP 5 — FILTER FUTURE MEMORIES
        # =====================================================

        memories = _filter_temporally_valid_memories(
            alert,
            recalled_memories,
        )

        memories = _select_relevant_memories(
            alert,
            memories,
        )

    else:

        # Memory OFF = cold-start reasoning.
        # Do not query Hindsight.
        memory_query = None
        recalled_memories = []
        memories = []

    # =========================================================
    # STEP 6 — FILTER FUTURE MEMORIES
    # =========================================================

    memories = _filter_temporally_valid_memories(
        alert,
        recalled_memories,
    )
    memories = _select_relevant_memories(
    alert,
    memories,
    )

    # =========================================================
    # STEP 7 — CREATE GROQ CLIENT
    # =========================================================

    client = _get_groq_client()

    model = os.getenv(
        "LLM_MODEL",
        "openai/gpt-oss-120b",
    )

    # =========================================================
    # STEP 8 — ASK GROQ FOR CANDIDATE DECISION
    # =========================================================

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """
You are a SOC alert triage reasoning assistant.

Return only the requested structured recommendation.

Do not perform security actions.

Do not invent evidence.

Historical analyst feedback must not be treated
as current alert evidence unless the current alert
contains the relevant indicator.

Future events must not influence earlier alerts.
""",
            },
            {
                "role": "user",
                "content": _build_reasoning_prompt(
                    alert,
                    asset,
                    account,
                    memories,
                ),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "soc_triage_verdict",
                "strict": True,
                "schema": VERDICT_SCHEMA,
            },
        },
    )

    # =========================================================
    # STEP 9 — READ GROQ RESPONSE
    # =========================================================

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Groq returned an empty response"
        )

    verdict = json.loads(content)

    # =========================================================
    # STEP 10 — RETURN COMPLETE ANALYSIS
    # =========================================================

    return {
        "alert": alert,
        "asset": asset,
        "account": account,

        # Only temporally valid memories are sent
        # as reasoning evidence.
        "memories": memories,

        "candidate_verdict": verdict,
    }
