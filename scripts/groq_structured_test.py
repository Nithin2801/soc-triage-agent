import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")


client = Groq(api_key=api_key)


response = client.chat.completions.create(
    model=model,
    temperature=0,
    messages=[
        {
            "role": "system",
            "content": """
You are a SOC alert triage reasoning assistant.

Analyze the supplied security alert and return a structured recommendation.

You are making a recommendation only.
Do not claim that an alert was automatically closed, blocked, or remediated.
""",
        },
        {
            "role": "user",
            "content": """
Analyze this synthetic SOC alert:

Alert type: Encoded PowerShell
Technique: T1059.001
Severity: medium
Asset: BKP-SRV-01
Asset role: backup_server
Account: svc-veeam
Parent process: Veeam.Backup.Service.exe
Time: 02:00
Description: Encoded PowerShell launched by the Veeam backup service
during the scheduled backup window.

Return the appropriate SOC recommendation.
""",
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "soc_triage_verdict",
            "strict": True,
            "schema": {
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
            },
        },
    },
)


content = response.choices[0].message.content

if not content:
    raise RuntimeError("Groq returned an empty response")


result = json.loads(content)


print("GROQ STRUCTURED OUTPUT TEST")
print("---------------------------")
print()
print(json.dumps(result, indent=2))
print()
print("GROQ STRUCTURED OUTPUT TEST PASSED")