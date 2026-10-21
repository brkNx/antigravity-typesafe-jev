#!/usr/bin/env python3
"""
TypeSafe Jev MCP Server for Google Antigravity (AGY)
Provides System 1 decision-making primitives over Model Context Protocol (stdio transport).
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

SERVER_INFO = {
    "name": "antigravity-typesafe-jev",
    "version": "1.0.0",
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


def _get_typesafe_client():
    api_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from typesafe_sdk import TypeSafeClient
        return TypeSafeClient(api_key=api_key)
    except Exception:
        return None


def handle_jev_choice(args: dict[str, Any]) -> str:
    state = args.get("state", "")
    instructions = args.get("instructions", "")
    criteria = args.get("criteria", {})

    client = _get_typesafe_client()
    if not client:
        return json.dumps({
            "status": "warning",
            "message": "TYPESAFE_API_KEY environment variable is not set. Please set TYPESAFE_API_KEY to execute live Jev model calls.",
            "dry_run": True,
            "choices_received": list(criteria.keys()),
        }, indent=2)

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
        return json.dumps({
            "status": "warning",
            "message": "TYPESAFE_API_KEY is not set. Provide an API key to execute live Jev scoring.",
            "dry_run": True,
            "rubric": criteria,
        }, indent=2)

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
        "score": ans.score,
        "confidence": ans.confidence,
        "probabilities": ans.probabilities,
    }, indent=2)


def handle_jev_noul(args: dict[str, Any]) -> str:
    state = args.get("state", "")
    instructions = args.get("instructions", "")

    client = _get_typesafe_client()
    if not client:
        return json.dumps({
            "status": "warning",
            "message": "TYPESAFE_API_KEY is not set. Provide an API key to execute live Jev Noul queries.",
            "dry_run": True,
        }, indent=2)

    from typesafe_sdk import Noul
    res = client.system_one(
        state=state,
        questions={
            "assertion": Noul(instructions=instructions)
        }
    )
    ans = res.answers["assertion"]
    return json.dumps({
        "status": "success",
        "noul": ans.noul,
        "is_likely_true": ans.noul >= 0.5,
    }, indent=2)


def handle_jev_guardrail(args: dict[str, Any]) -> str:
    action = args.get("action", "")
    context = args.get("context", "")

    client = _get_typesafe_client()
    if not client:
        destructive_patterns = ["rmdir /s", "rm -rf", "drop table", "git reset --hard", "format ", "dd if="]
        is_suspicious = any(p in action.lower() for p in destructive_patterns)
        return json.dumps({
            "status": "fallback_heuristic",
            "warning": "TYPESAFE_API_KEY is not set. Using built-in basic pattern matching.",
            "action": action,
            "risk_detected": is_suspicious,
            "allow_execution": not is_suspicious,
        }, indent=2)

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
