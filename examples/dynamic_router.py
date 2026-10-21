#!/usr/bin/env python3
"""
Dynamic Model and Subagent Router using Jev Choice.
Routes incoming user instructions to flash_lite, flash, or pro models in ~100ms.
"""
import os
from typesafe_sdk import TypeSafeClient, Choice

def route_request(user_prompt: str) -> str:
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("[ROUTER] TYPESAFE_API_KEY not found. Defaulting to 'flash'.")
        return "flash"

    client = TypeSafeClient(api_key=api_key)
    res = client.system_one(
        state=f"User Prompt: {user_prompt}",
        questions={
            "model_route": Choice(
                instructions="Which model tier should execute this coding task?",
                criteria={
                    "flash_lite": "File search, directory discovery, log parsing, documentation lookup",
                    "flash": "Single-file edit, simple bugfix, unit test execution, small explanation",
                    "pro": "Multi-file refactoring, complex system design, security audit, database migration"
                }
            )
        }
    )
    choice = res.answers["model_route"]
    print(f"[ROUTER] Assigned model: {choice.choice} (Confidence: {choice.confidence:.2%})")
    return choice.choice

if __name__ == "__main__":
    prompts = [
        "Find where the database connection string is configured in this repository.",
        "Fix the typo in the login button label.",
        "Redesign our entire distributed cache architecture to handle failover."
    ]
    for p in prompts:
        print(f"\nPrompt: '{p}'")
        route_request(p)
