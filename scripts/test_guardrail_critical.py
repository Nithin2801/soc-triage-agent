from backend.app.guardrails import (
    apply_critical_severity_guardrail,
)


alert = {
    "alert_id": "TEST-CRITICAL-001",
    "severity": "critical",
}


candidate_verdict = {
    "verdict": "Likely Benign",
    "confidence": 0.95,
    "reasoning": "Historical memory appears to support this activity.",
}


print("CRITICAL SEVERITY GUARDRAIL TEST")
print("--------------------------------")
print()

print("BEFORE GUARDRAIL:")
print(candidate_verdict)

print()

result = apply_critical_severity_guardrail(
    alert,
    candidate_verdict,
)

print("AFTER GUARDRAIL:")
print(result)

print()

assert result["verdict"] == "Escalate"
assert result["guardrail_override"] is True
assert (
    result["guardrail_reason"]
    == "Critical severity prevents a Likely Benign recommendation."
)

print("CRITICAL SEVERITY GUARDRAIL TEST PASSED")