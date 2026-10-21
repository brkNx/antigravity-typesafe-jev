#!/usr/bin/env python3
"""
AGY Pre-Tool Execution Hook:
Inspects shell commands before execution using Jev Noul calibrated probability.
"""
import sys
import os
import json

def audit_command(command_str: str) -> bool:
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("[JEV GUARDRAIL] Warning: TYPESAFE_API_KEY not set. Falling back to local heuristic.")
        destructive_patterns = ["rmdir /s", "rm -rf", "drop table", "git reset --hard", "format "]
        return not any(p in command_str.lower() for p in destructive_patterns)

    from typesafe_sdk import TypeSafeClient, Noul
    client = TypeSafeClient(api_key=api_key)

    res = client.system_one(
        state=f"Shell Command: {command_str}",
        questions={
            "is_destructive": Noul(
                instructions="Will this command cause unrecoverable data loss, delete source repositories, or format drives?"
            )
        }
    )
    destructive_prob = res.answers["is_destructive"].noul
    print(f"[JEV GUARDRAIL] Destructive probability: {destructive_prob:.2%}")
    return destructive_prob < 0.20

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "git status"
    is_safe = audit_command(cmd)
    if is_safe:
        print(f"[JEV GUARDRAIL] Command approved: '{cmd}'")
        sys.exit(0)
    else:
        print(f"[JEV GUARDRAIL] Execution blocked! Dangerous command detected: '{cmd}'")
        sys.exit(1)
