---
name: typesafe-jev
description: System 1 AI decision-making with TypeSafe Jev. Enables sub-second routing, guardrails, rubric scoring, and binary probability evaluations without token-generation overhead. Use for fast agent decisions, pre-tool validation, context compaction, and building with typesafe-sdk.
---

# TypeSafe Jev (System One AI) Skill for Antigravity

Jev is the first production **System 1** AI model, released by TypeSafe AI (founded by Diogo Almeida). Unlike generative LLMs (System 2: Gemini, Claude, GPT), Jev does not generate text token-by-token. Instead, it evaluates context against typed primitives in 70–300 ms, returning calibrated probabilities and confidence scores with zero schema hallucinations.

---

## 1. Core Primitives

Jev operates on three core discriminative primitives:

### 1. `Choice` (Categorical Selection)
Routes inputs to discrete categories.
- Returns: `choice` (str), `confidence` (float 0.0-1.0), `probabilities` (dict[str, float]).
- Use cases: Model selection, subagent delegation, intent classification.

### 2. `Score` (Rubric Rating)
Rates inputs against an ordered scale.
- Returns: `score` (float), `confidence` (float), `probabilities` (dict[str, float]).
- Use cases: Urgency triage, complexity assessment, quality gate scoring.

### 3. `Noul` (Binary Assertion / Probability)
Evaluates whether a condition or statement is true.
- Returns: `noul` (calibrated float probability between 0.0 and 1.0).
- Use cases: Safety guardrails, bug vs feature detection, confirmation thresholds.

---

## 2. Using `typesafe_sdk` in Python

Install:
```bash
pip install typesafe-sdk
```

Environment variable:
```bash
export TYPESAFE_API_KEY="ts_..."  # Windows: set TYPESAFE_API_KEY="ts_..."
```

Example Python usage:
```python
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul

client = TypeSafeClient()

# Execute System 1 decision call
res = client.system_one(
    state="git push origin main --force",
    questions={
        "is_dangerous": Noul(
            instructions="Does this command risk overwriting shared remote git history?"
        ),
        "risk_level": Score(
            instructions="Rate the operational risk of running this command.",
            criteria=["low", "medium", "high", "critical"]
        )
    }
)

is_dangerous_prob = res.answers["is_dangerous"].noul
risk_score = res.answers["risk_level"].score

print(f"Dangerous: {is_dangerous_prob:.2f}, Risk Score: {risk_score:.2f}")
```

---

## 3. AGY Integration Patterns

### Pattern A: AGY Pre-Tool Guardrail Hook
Verify actions before executing shell commands or destructive edits in Antigravity:
```python
# .gemini/hooks/guardrail.py
import sys, json
from typesafe_sdk import TypeSafeClient, Noul

client = TypeSafeClient()
action = sys.argv[1]

res = client.system_one(
    state=f"Proposed Action: {action}",
    questions={
        "is_destructive": Noul(
            instructions="Does this command delete data, reset working tree, or harm the OS?"
        )
    }
)

if res.answers["is_destructive"].noul > 0.25:
    print(f"Execution halted: High destruction risk ({res.answers['is_destructive'].noul:.2f})")
    sys.exit(1)
```

### Pattern B: AGY MCP Tools
AGY is pre-configured with the `jev` MCP server:
- `jev_choice`: Fast subagent or path selection.
- `jev_score`: Task complexity assessment.
- `jev_noul`: Fast boolean assertion.
- `jev_guardrail`: Pre-execution command risk audit.

Call via MCP tool calls directly in agent workflows to avoid multi-second generative LLM reasoning for pure boolean/routing decisions.
