<div align="center">

# 🧬 six6

**6-Module Organic AI Agent Ecosystem built with absolute file-system decoupling.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw/openclaw)
[![GitHub stars](https://img.shields.io/github/stars/ythx-101/six6?style=social)](https://github.com/ythx-101/six6)

*Modular · Plug-and-Play · State via File System · Works everywhere*

[Architecture](#-architecture) · [Modules](#-the-6-modules) · [Quick Start](#-quick-start)

</div>

---

## 😤 Problem

```
You: "I want an AI Agent that can think, remember, and generate ideas."
Current frameworks: "Here is a massive 1GB monolithic orchestrator with tight Python couplings."
```

six6 decomposes the core cognitive functions of an AI Agent into **6 independent modules**. They do not import each other. They do not share memory space. They communicate entirely through a standardized set of files (Markdown & JSONL).

To make this reusable for OpenClaw users, the repository also includes three supporting layers that sit underneath the six modules:

- `protocol/`: file contracts and schemas.
- `runtime/`: init, validate, doctor, and pulse entrypoints.
- `distribution/`: packaging guidance for install and migration.

You can install just the memory system, or you can install the entire suite to create a living, breathing organic AI entity.

## 🧬 Architecture

Absolute decoupling is our core principle:
- **No Python imports between modules.**
- **Standardized data flow** via Markdown (for cognition/memory) and JSONL (for queues/seeds).

Read the detailed [ARCHITECTURE.md](ARCHITECTURE.md) for data flow specifications.

## 🧱 The 6 Modules

1. **`skill-memory` (Cerebral Cortex)**
   - Manages short-term context (`NOW.md`) and long-term daily episodic memory (`memory/YYYY-MM-DD.md`).
   - Maintains the core cognitive summary (`MEMORY.md`).

2. **`skill-meditation` (Reflection)**
   - Deep reflection mechanism. Runs nightly to synthesize the day's memory into the core `MEMORY.md`.

3. **`skill-daydream` (Divergent Ideation)**
   - Randomly samples historical memory fragments during idle time to generate serendipitous ideas, outputting them as JSON objects to the Topic Lab.

4. **`skill-topic-lab` (Greenhouse / Farm)**
   - Manages the lifecycle of generated ideas (seeds).
   - Tracks maturity. When a seed hits >80% maturity, it automatically triggers external outputs (e.g., creating a GitHub Issue).

5. **`skill-autoloop` (Action Center)**
   - The task queuing and execution hub.
   - Manages `inbox.jsonl` and handles escalation protocols (e.g., `needs-decision`).

6. **`skill-monitor` (Life Support / Heartbeat)**
   - The chronometer and health checker. Manages system pulses and triggers for the other modules.

## 🚀 Quick Start

1. Clone the repository into your skills directory:
   ```bash
   git clone https://github.com/ythx-101/six6.git
   ```
2. Check the `ARCHITECTURE.md` file to understand the required file structures.
3. Hook any or all modules into your agent's cron or trigger system.
4. Bootstrap a writable base directory:
   ```bash
   python3 runtime/scripts/six6.py init --base-dir /path/to/agent/root
   ```
5. Validate protocol files:
   ```bash
   python3 runtime/scripts/six6.py validate --base-dir /path/to/agent/root
   ```
6. Try the included sample base directory:
   ```bash
   python3 runtime/scripts/six6.py validate --base-dir demo
   python3 runtime/scripts/six6.py pulse heartbeat --base-dir demo
   ```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
