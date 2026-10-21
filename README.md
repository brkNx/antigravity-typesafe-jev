# Antigravity TypeSafe Jev (System 1 AI) Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![TypeSafe SDK](https://img.shields.io/badge/typesafe--sdk-v0.7.5-orange)](https://typesafe.ai)
[![Platform](https://img.shields.io/badge/platform-Google%20Antigravity-green)](https://antigravity.google)

Production integration of **TypeSafe AI's Jev** (the first public **System 1** decision model) into the **Google Antigravity (`agy`)** agent platform and Model Context Protocol (MCP) ecosystem.

---

## ⚡ Why System 1 in Antigravity?

Traditional AI agent loops rely on generative Large Language Models (Gemini, Claude, GPT) for every step. These are **System 2** thinkers:
- Slower latency (multiple seconds to generate tokens)
- High cost per token
- Prone to JSON schema formatting hallucinations when only a simple boolean or categorical decision is needed.

**Jev** (by TypeSafe AI) is a **System 1** model that skips autoregressive text generation entirely:
- **Sub-second decisions:** 70–300 ms response times.
- **Calibrated probabilities:** Returns confidence scores and probability distributions trained via RLCD (Reinforcement Learning for Calibrated Decisions).
- **Type-safe primitives:** `Choice`, `Score`, and `Noul` (binary assertions) with zero schema drift.

```
                      [User Prompt / Action]
                               │
                               ▼
                   ┌───────────────────────┐
                   │ Jev (System 1: ~100ms)│
                   └───────────┬───────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
    [Choice: Router]    [Noul: Guardrail]   [Score: Complexity]
    flash_lite vs pro   Is this command     Triage low vs critical
    subagent selection  destructive?        priority
```

---

## 📦 What's Included

1. **MCP Server (`src/mcp_server.py`)**:
   Standard JSON-RPC 2.0 stdio transport exposing 4 System 1 tools:
   - `jev_choice`: Categorical classification with calibrated confidence.
   - `jev_score`: Ordered rubric scoring.
   - `jev_noul`: Binary true/false probability (0.0 to 1.0).
   - `jev_guardrail`: Pre-execution command and file mutation safety check.
2. **AGY Skill (`skills/typesafe-jev/SKILL.md`)**:
   Reusable skill for Antigravity agents detailing architecture, code conventions, and System 1 patterns.
3. **Executable Examples (`examples/`)**:
   - `quickstart.py`: End-to-end usage of `Choice`, `Score`, and `Noul`.
   - `guardrail_hook.py`: AGY pre-tool hook intercepting dangerous shell commands.
   - `dynamic_router.py`: Sub-second routing of user prompts to `flash_lite`, `flash`, or `pro` tiers.

---

## 🚀 Quickstart

### 1. Requirements & Installation

```bash
git clone https://github.com/brkNx/antigravity-typesafe-jev.git
cd antigravity-typesafe-jev
pip install -r requirements.txt
```

### 2. Set API Key

Get your API key from [TypeSafe AI](https://typesafe.ai):

```bash
# Linux / macOS
export TYPESAFE_API_KEY="ts_your_api_key_here"

# Windows PowerShell
$env:TYPESAFE_API_KEY="ts_your_api_key_here"
```

---

## 🔌 Connecting to Google Antigravity (`agy`)

Add the server to your `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "jev": {
      "command": "python",
      "args": [
        "/path/to/antigravity-typesafe-jev/src/mcp_server.py"
      ],
      "env": {
        "TYPESAFE_API_KEY": "YOUR_TYPESAFE_API_KEY"
      }
    }
  }
}
```

### Installing the Skill in AGY

Copy the skill to your Antigravity skills directory:

```bash
# Windows
Copy-Item -Path "skills\typesafe-jev" -Destination "$env:USERPROFILE\.gemini\config\skills\" -Recurse -Force

# Linux / macOS
cp -r skills/typesafe-jev ~/.gemini/config/skills/
```

---

## 🛡️ Pre-Tool Hook Example

To protect your environment against catastrophic agent actions (`rm -rf`, uncommitted git wipes, production dropping), configure an AGY pre-tool hook:

```bash
python examples/guardrail_hook.py "git reset --hard HEAD~5"
# [JEV GUARDRAIL] Destructive probability: 96.40%
# [JEV GUARDRAIL] Execution blocked! Dangerous command detected: 'git reset --hard HEAD~5'
```

---

## 📜 References

- [Introducing System One Models & Jev (TypeSafe AI Blog)](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [Google Antigravity Documentation](https://antigravity.google)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)

---

## 📄 License

MIT © [brkNx](https://github.com/brkNx)
