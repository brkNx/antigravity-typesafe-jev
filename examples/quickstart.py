#!/usr/bin/env python3
"""
Quickstart example using TypeSafe Jev System 1 primitives.
"""
import os
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul

# Ensure TYPESAFE_API_KEY is set
api_key = os.environ.get("TYPESAFE_API_KEY")
if not api_key:
    print("Please set your TYPESAFE_API_KEY environment variable.")
    exit(1)

client = TypeSafeClient(api_key=api_key)

# Context state
task = "Refactor user authentication module to support OAuth2 PKCE flow."

# 1. Choice Primitive: Select the appropriate specialist subagent
print("\n[1] Evaluating Specialist Subagent...")
choice_res = client.system_one(
    state=task,
    questions={
        "specialist": Choice(
            instructions="Which engineering role is best suited for this task?",
            criteria={
                "security": "Auth, cryptography, tokens, OAuth, vulnerabilities",
                "frontend": "UI components, styling, animations, layout",
                "devops": "CI/CD, Docker, Kubernetes, cloud infra, deployment",
            }
        )
    }
)
ans_choice = choice_res.answers["specialist"]
print(f"Selected: {ans_choice.choice} (Confidence: {ans_choice.confidence:.2f})")

# 2. Score Primitive: Assess task complexity
print("\n[2] Scoring Task Complexity...")
score_res = client.system_one(
    state=task,
    questions={
        "complexity": Score(
            instructions="How complex is this refactoring task?",
            criteria=["trivial", "moderate", "complex", "high-risk-architectural"]
        )
    }
)
ans_score = score_res.answers["complexity"]
print(f"Complexity Score: {ans_score.score:.2f} (Confidence: {ans_score.confidence:.2f})")

# 3. Noul Primitive: Binary condition probability
print("\n[3] Checking Breaking Change Probability...")
noul_res = client.system_one(
    state=task,
    questions={
        "is_breaking": Noul(
            instructions="Does this change risk breaking existing active user sessions?"
        )
    }
)
ans_noul = noul_res.answers["is_breaking"]
print(f"Breaking Change Probability: {ans_noul.noul:.2f}")
