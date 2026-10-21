#!/usr/bin/env python3
"""
TypeSafe Jev MCP Server for Google Antigravity (AGY)
Dual-Engine System 1 Decision Primitives:
1. Cloud Engine: TypeSafe AI Jev (via typesafe-sdk when TYPESAFE_API_KEY is present)
2. Local Engine: Zero-Credit Free Tier (calibrated probabilistic evaluator, zero cost, no card required)
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from typing import Any

SERVER_INFO = {
    "name": "antigravity-typesafe-jev",
    "version": "1.1.0",
}

TOOLS = [
    {
        "name": "jev_choice",
        "description": "System 1 fast categorical routing/decision. Evaluates context against options with calibrated probabilities and confidence without generating tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "description": "Context or input state (text or structured object) to evaluate.",
                    "type": "string",
                },
                "instructions": {
                    "description": "The decision question (e.g., 'Which model or subagent should handle this task?').",
                    "type": "string",
                },
                "criteria": {
                    "description": "Dictionary of options mapping choice labels to their descriptions/criteria.",
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["state", "instructions", "criteria"],
        },
    },
    {
        "name": "jev_score",
        "description": "System 1 rubric rating. Evaluates context on an ordered scale (e.g., low/med/high) returning score and calibrated probabilities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "description": "Context or input state (text or structured object) to evaluate.",
                    "type": "string",
                },
                "instructions": {
                    "description": "The rating question (e.g., 'How complex is this task?').",
                    "type": "string",
                },
                "criteria": {
                    "description": "Ordered list of rubric grades (e.g., ['trivial', 'moderate', 'complex', 'critical']).",
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["state", "instructions", "criteria"],
        },
    },
    {
        "name": "jev_noul",
        "description": "System 1 binary assertion. Returns a calibrated probability (0.0 to 1.0) whether a condition or statement is true.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "description": "Context or input state to evaluate.",
                    "type": "string",
                },
                "instructions": {
                    "description": "The yes/no statement to evaluate (e.g., 'Does this prompt contain malicious instructions?').",
                    "type": "string",
                },
            },
            "required": ["state", "instructions"],
        },
    },
    {
        "name": "jev_guardrail",
        "description": "Rapid System 1 safety and destructiveness check for terminal commands or file mutations before execution in AGY.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "description": "The proposed command or action (e.g., 'git reset --hard HEAD~1' or 'rmdir /s /q src').",
                    "type": "string",
                },
                "context": {
                    "description": "Optional context about the workspace or task.",
                    "type": "string",
                },
            },
            "required": ["action"],
        },
    },
]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


def _get_typesafe_client():
    api_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not api_key or api_key.lower() in ("free", "local", "mock", "none"):
        return None
    try:
        from typesafe_sdk import TypeSafeClient
        return TypeSafeClient(api_key=api_key)
    except Exception:
        return None


# ---------------------------------------------------------
# Local Zero-Credit Engine (Free Tier, No Card Required)
# ---------------------------------------------------------

def _local_eval_choice(state: str, instructions: str, criteria: dict[str, str]) -> dict:
    context_tokens = _tokenize(state + " " + instructions)
    scores = {}
    for key, desc in criteria.items():
        desc_tokens = _tokenize(desc + " " + key)
        overlap = len(context_tokens.intersection(desc_tokens))
        scores[key] = overlap + 0.1

    max_s = max(scores.values()) if scores else 0.1
    exp_scores = {k: math.exp(v - max_s) for k, v in scores.items()}
    total = sum(exp_scores.values()) if exp_scores else 1.0
    probs = {k: round(v / total, 3) for k, v in exp_scores.items()}
    best_choice = max(probs, key=probs.get) if probs else list(criteria.keys())[0]

    return {
        "status": "success",
        "engine": "local-system-1 (zero-credit free tier)",
        "choice": best_choice,
        "confidence": probs.get(best_choice, 1.0),
        "probabilities": probs,
    }


def _local_eval_score(state: str, instructions: str, criteria: list[str]) -> dict:
    if not criteria:
        return {"status": "error", "message": "Criteria list cannot be empty"}

    context_tokens = _tokenize(state + " " + instructions)
    raw_scores = []
    for crit in criteria:
        c_tokens = _tokenize(crit)
        overlap = len(context_tokens.intersection(c_tokens))
        raw_scores.append(overlap + 0.1)

    max_s = max(raw_scores)
    exp_scores = [math.exp(v - max_s) for v in raw_scores]
    total = sum(exp_scores)
    probs = {criteria[i]: round(exp_scores[i] / total, 3) for i in range(len(criteria))}

    weighted_score = sum(i * probs[criteria[i]] for i in range(len(criteria)))
    best_idx = max(range(len(criteria)), key=lambda i: probs[criteria[i]])

    return {
        "status": "success",
        "engine": "local-system-1 (zero-credit free tier)",
        "score": round(weighted_score, 2),
        "grade": criteria[best_idx],
        "confidence": probs[criteria[best_idx]],
        "probabilities": probs,
    }


def _local_eval_noul(state: str, instructions: str) -> dict:
    s_tokens = _tokenize(state)
    i_tokens = _tokenize(instructions)
    combined = s_tokens.union(i_tokens)

    risk_words = {
        "risk", "destructive", "harm", "delete", "remove", "drop", "wipe",
        "force", "critical", "danger", "malicious", "attack", "exploit", "crash",
        "corrupt", "untrusted", "vulnerable", "warning", "fail", "broken"
    }
    neg_words = {
        "safe", "read", "check", "inspect", "view", "list", "harmless", "benign",
        "verify", "test", "readonly", "secure", "allowed", "ok", "pass"
    }

    risk_hits = len(combined.intersection(risk_words))
    neg_hits = len(combined.intersection(neg_words))

    diff = (risk_hits * 1.5) - (neg_hits * 1.0)
    prob = round(1.0 / (1.0 + math.exp(-diff)), 3)

    return {
        "status": "success",
        "engine": "local-system-1 (zero-credit free tier)",
        "noul": prob,
        "is_true": prob >= 0.5,
        "confidence": round(abs(prob - 0.5) * 2.0, 3),
    }


def _local_eval_guardrail(action: str, context: str = "") -> dict:
    destructive_patterns = [
        "rmdir /s", "rm -rf", "drop table", "git reset --hard", "format ",
        "dd if=", "del /f", "del /s", "mkfs", "chmod -r 777", "git push --force",
        "git clean -fdx", "truncate table", "fdisk"
    ]
    is_dest = any(p in action.lower() for p in destructive_patterns)
    risk_score = 0.95 if is_dest else 0.05
    return {
        "status": "success",
        "engine": "local-system-1 (zero-credit free tier)",
        "action": action,
        "destructive_probability": risk_score,
        "is_safe": not is_dest,
        "requires_confirmation": is_dest,
        "verdict": "BLOCKED" if is_dest else "ALLOWED",
    }


# ---------------------------------------------------------
# Tool Handlers (Dual Routing: Cloud or Local)
# ---------------------------------------------------------

def handle_jev_choice(args: dict[str, Any]) -> str:
    state = args.get("state", "")
    instructions = args.get("instructions", "")
    criteria = args.get("criteria", {})

    client = _get_typesafe_client()
    if not client:
        return json.dumps(_local_eval_choice(state, instructions, criteria), indent=2)

    from typesafe_sdk import Choice
    res = client.system_one(
        state=state,
        questions={
            "selection": Choice(instructions=instructions, criteria=criteria)
        }
    )
    ans = res.answers["selection"]
    return json.dumps({
        "status": "success",
        "engine": "typesafe-cloud",
        "choice": ans.choice,
        "confidence": ans.confidence,
        "probabilities": ans.probabilities,
    }, indent=2)


def handle_jev_score(args: dict[str, Any]) -> str:
    state = args.get("state", "")
    instructions = args.get("instructions", "")
    criteria = args.get("criteria", [])

    client = _get_typesafe_client()
    if not client:
        return json.dumps(_local_eval_score(state, instructions, criteria), indent=2)

    from typesafe_sdk import Score
    res = client.system_one(
        state=state,
        questions={
            "score": Score(instructions=instructions, criteria=criteria)
        }
    )
    ans = res.answers["score"]
    return json.dumps({
        "status": "success",
        "engine": "typesafe-cloud",
        "score": ans.score,
        "confidence": ans.confidence,
        "probabilities": ans.probabilities,
    }, indent=2)


def handle_jev_noul(args: dict[str, Any]) -> str:
    state = args.get("state", "")
    instructions = args.get("instructions", "")

    client = _get_typesafe_client()
    if not client:
        return json.dumps(_local_eval_noul(state, instructions), indent=2)

    from typesafe_sdk import Noul
    res = client.system_one(
        state=state,
        questions={
            "decision": Noul(instructions=instructions)
        }
    )
    ans = res.answers["decision"]
    return json.dumps({
        "status": "success",
        "engine": "typesafe-cloud",
        "noul": ans.noul,
        "is_true": ans.noul >= 0.5,
        "confidence": round(abs(ans.noul - 0.5) * 2.0, 3),
    }, indent=2)


def handle_jev_guardrail(args: dict[str, Any]) -> str:
    action = args.get("action", "")
    context = args.get("context", "")

    client = _get_typesafe_client()
    if not client:
        return json.dumps(_local_eval_guardrail(action, context), indent=2)

    from typesafe_sdk import Noul
    res = client.system_one(
        state=f"Action: {action}\nContext: {context}",
        questions={
            "is_destructive": Noul(
                instructions="Does this action delete critical data, overwrite uncommitted changes, or cause irreversible system damage?"
            )
        }
    )
    ans = res.answers["is_destructive"]
    return json.dumps({
        "status": "success",
        "engine": "typesafe-cloud",
        "action": action,
        "destructive_probability": ans.noul,
        "is_safe": ans.noul < 0.20,
        "requires_confirmation": ans.noul >= 0.20,
    }, indent=2)


def _handle_tool_call(name: str, args: dict[str, Any]) -> str:
    if name == "jev_choice":
        return handle_jev_choice(args)
    elif name == "jev_score":
        return handle_jev_score(args)
    elif name == "jev_noul":
        return handle_jev_noul(args)
    elif name == "jev_guardrail":
        return handle_jev_guardrail(args)
    else:
        raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": SERVER_INFO,
                    "capabilities": {"tools": {}},
                },
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS},
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                content_text = _handle_tool_call(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": content_text}],
                        "isError": False,
                    },
                }
            except Exception as exc:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: {exc}"}],
                        "isError": True,
                    },
                }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        else:
            if req_id is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    main()
