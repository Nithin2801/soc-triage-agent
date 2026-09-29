from backend.app.guardrails import (
    apply_critical_asset_guardrail,
)


alert = {
    "alert_id": "TEST-CRITICAL-ASSET-001",
    "severity": "medium",
}


asset = {
    "asset_id": "DC-01",
    "criticality": "critical",
}


candidate_verdict = {
    "verdict": "Likely Benign",
    "confidence": 0.95,
    "reasoning": (
        "Historical memory appears to support "
        "this activity."
    ),
}


print("CRITICAL ASSET GUARDRAIL TEST")
print("------------------------------")
print()

print("BEFORE GUARDRAIL:")
print(candidate_verdict)

print()

result = apply_critical_asset_guardrail(
    alert,
    asset,
    candidate_verdict,
)

print("AFTER GUARDRAIL:")
print(result)

print()

assert result["verdict"] == "Escalate"

assert result["guardrail_override"] is True

assert (
    result["guardrail_reason"]
    == (
        "Critical asset prevents a Likely Benign "
        "recommendation."
    )
)

print("CRITICAL ASSET GUARDRAIL TEST PASSED")