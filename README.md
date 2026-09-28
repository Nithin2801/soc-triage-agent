# SOC Alert Triage Agent

An AI-assisted SOC alert triage agent that learns from analyst feedback using persistent Hindsight memory.

## Project Goal

The agent helps a Security Operations Center (SOC) analyst triage repetitive security alerts.

It:

1. Receives a security alert.
2. Retrieves relevant security context.
3. Recalls previous analyst experience from Hindsight.
4. Reasons over the current alert and recalled experience.
5. Applies deterministic safety guardrails.
6. Produces a recommendation:
   - Likely Benign
   - Investigate
   - Escalate
7. Allows the analyst to approve or override the recommendation.
8. Stores the analyst feedback as persistent experience for future alerts.

## Architecture

Browser
    ↓
Frontend
    ↓
FastAPI Backend
    ↓
Agent Orchestrator
    ├── Security Context Tools
    ├── Hindsight Memory
    ├── Groq LLM
    └── Guardrails
    ↓
Recommendation

## Technology

- Python
- FastAPI
- HTML / CSS / JavaScript
- Hindsight
- Groq
- SQLite
- Git / GitHub

## Important Design Principle

SQLite stores operational application state.

Hindsight stores persistent experiential knowledge learned from analyst feedback.

The agent recommends actions; it does not automatically close, block, or isolate security alerts.

## Project Status

Initial development and environment setup.