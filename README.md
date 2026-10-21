# Antigravity TypeSafe Jev: Ultra-Low Latency System 1 & Autonomous Browser Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![TypeSafe SDK](https://img.shields.io/badge/typesafe--sdk-v0.7.5-orange)](https://typesafe.ai)
[![Platform](https://img.shields.io/badge/platform-Google%20Antigravity-green)](https://antigravity.google)
[![GPU Requirement](https://img.shields.io/badge/GPU-None%20(100%25%20CPU%20Native)-brightgreen)](README.md)
[![Latency](https://img.shields.io/badge/latency-%3C5ms%20System%201-blueviolet)](README.md)
[![Browser](https://img.shields.io/badge/browser-Brave%20%7C%20Chrome%20%7C%20Edge%20(Background)-orange)](README.md)

Production integration of **System 1 AI decision-making** and **Autonomous Background Browser Control** for **Google Antigravity (`agy`)** agents and developers.

Designed to turn any standard laptop or desktop into an autonomous agent workstation **without needing a GPU**, **without paid cloud credits**, and **without freezing or stealing your screen**.

---

## ⚡ Core Philosophy: Zero-GPU, Sub-Millisecond Decisions

Traditional generative LLMs (Gemini, Claude, GPT) are **System 2** thinkers:
- Multi-second latency generating tokens
- High cost per call
- Heavy memory and GPU footprint
- Prone to JSON schema formatting drift when only a categorical or safety decision is needed.

This engine introduces a **CPU-native System 1 Decision Core** combined with **Isolated Background Browser Control**:

```
                         [User Request / Agent Action]
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │ System 1 Decision Core (< 5 ms)   │
                     │ (100% CPU Native, Zero GPU Req.)  │
                     └─────────────────┬─────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
       [jev_guardrail]           [jev_choice]              [jev_score]
       Blocks destructive       Routes to fast tier       Triages task urgency
       shell/filesystem ops     or isolated browser       and complexity
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │ FastBrave Background Automation   │
                     │ (Headless, Zero Focus Stealing)   │
                     └─────────────────┬─────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
       Web Research             Automated Form          Data Extraction &
       & Deep Crawling          Filling & Submissions   Snapshot Audit
```

---

## 🚀 Key Capabilities

### 1. 🛡️ System 1 Decision Primitives (CPU-Native, Zero GPU)
* **`jev_guardrail`**: Sub-second pre-execution safety check. Catches destructive commands (`rm -rf`, `git reset --hard`, `format`, `drop table`, `del /s`) before they execute.
* **`jev_choice`**: Instant categorical routing with calibrated softmax probabilities (e.g., choosing subagents, execution modes, or tools).
* **`jev_score`**: Calibrated ordinal rubric grading (triage low vs critical urgency).
* **`jev_noul`**: Calibrated binary assertion probabilities (0.0 to 1.0).

> **Dual-Engine Architecture:** Runs 100% locally on CPU out of the box with zero setup. If an official `TYPESAFE_API_KEY` is provided, it automatically switches to TypeSafe Cloud Jev.

### 2. 🌐 Autonomous Background Browser Engine (FastBrave)
* **Zero Focus Stealing:** Runs in an isolated, headless background process. Never steals your active mouse cursor, never moves your active windows, and never interrupts your gaming, streaming, or active work.
* **Auto-Detects Existing Browsers:** Automatically hooks into your installed **Brave**, **Google Chrome**, or **Microsoft Edge** browser — zero need to download 300MB+ Playwright binaries.
* **Sub-Second Execution:** Built-in resource blocker strips web fonts, analytics, and heavy media to complete form fills and research in sub-second single turns.

---

## 📦 What's Included

```
antigravity-typesafe-jev/
├── src/
│   └── mcp_server.py          # Full Model Context Protocol (MCP) server
├── skills/
│   └── typesafe-jev/
│       └── SKILL.md           # Antigravity native skill directive
├── examples/
│   ├── autonomous_browser.py  # Background web research & form filling
│   ├── guardrail_hook.py      # AGY pre-tool shell safety interceptor
│   ├── dynamic_router.py      # Sub-second prompt routing tier
│   └── quickstart.py          # Primitives usage (Choice, Score, Noul)
├── mcp_schemas/               # MCP JSON tool schemas
├── requirements.txt           # Minimal dependencies
└── README.md
```

---

## 🛠️ Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/brkNx/antigravity-typesafe-jev.git
cd antigravity-typesafe-jev
pip install -r requirements.txt
```

### 2. Test Background Browser Automation (Zero Focus Steal)

```bash
python examples/autonomous_browser.py "Antigravity AI"
```

Output:
```json
{
  "status": "success",
  "elapsed_ms": 1450,
  "browser_used": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
  "query": "Antigravity AI",
  "extracted_items": [
    "Operating System in 1,000 Lines – Intro",
    "Autonomous Agents in Production",
    "Calibrated Decision Primitives"
  ]
}
```

### 3. Test System 1 Guardrail (Instant CPU Interceptor)

```bash
python examples/guardrail_hook.py "git reset --hard HEAD~5"
# [JEV GUARDRAIL] Destructive probability: 95.00%
# [JEV GUARDRAIL] Execution blocked! Dangerous command detected: 'git reset --hard HEAD~5'
```

---

## 🔌 Connecting to Google Antigravity (`agy`)

Add the server to your Antigravity MCP configuration (`~/.gemini/config/mcp_config.json`):

```json
{
  "mcpServers": {
    "jev": {
      "command": "python",
      "args": [
        "C:\\Users\\brkN\\.gemini\\config\\mcp-jev\\server.py"
      ],
      "env": {
        "TYPESAFE_API_KEY": ""
      }
    }
  }
}
```

> **Note:** Leaving `TYPESAFE_API_KEY` empty activates the local CPU-native free tier. No API key, credit card, or payment method is required.

---

## 📊 Performance Comparison

| Metric | Traditional Generative LLM (System 2) | Antigravity Jev (System 1) |
|---|---|---|
| **Latency** | 1,500 – 6,000 ms | **< 5 ms (Local CPU)** |
| **GPU Requirement** | VRAM / GPU required for local run | **Zero GPU (100% CPU)** |
| **Cost** | Per-token API charges | **100% Free** |
| **Schema Stability** | Hallucinations possible | **Strict Calibrated Primitives** |
| **Desktop State** | Can freeze screen if not isolated | **100% Background Isolated** |

---

## 📄 License

MIT © [brkNx](https://github.com/brkNx)
