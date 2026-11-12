<div align="center">

# 🧬 six6

**6-Module Organic AI Agent Ecosystem built with absolute file-system decoupling.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw/openclaw)
[![CI](https://github.com/ythx-101/six6/actions/workflows/ci.yml/badge.svg)](https://github.com/ythx-101/six6/actions/workflows/ci.yml)
[![GitHub stars](https://img.shields.io/github/stars/ythx-101/six6?style=social)](https://github.com/ythx-101/six6)

*Modular · Plug-and-Play · State via File System · Works everywhere*

[Who is it for](#-who-is-it-for) · [Requirements](#-requirements) · [Quick Start](#-quick-start) · [Usage](#-usage-example) · [Architecture](#-architecture) · [Modules](#-the-6-modules) · [Comparison](#-comparison) · [FAQ](#-faq)

</div>

**six6** is a zero-dependency, file-based memory and cognition toolkit for AI agents (built for OpenClaw). Six independent Python modules give an agent short- and long-term memory, nightly reflection, daydream-style idea generation, an idea lifecycle "topic lab", an inbox task loop, and a cron heartbeat — all communicating only through Markdown and JSONL files.

中文：six6 是一套给 AI Agent 用的文件系统记忆与认知模块（OpenClaw Skill），6 个模块互不依赖，只靠 Markdown / JSONL 文件交换状态，无需向量数据库、无需第三方依赖。

---

## 🎯 Who is it for

适用场景:

- You want to add persistent AI agent memory (long-term, file-based) to OpenClaw or your own agent.
- You prefer human-readable, git-diffable Markdown memory over a vector store.
- You want low-cost "background thinking" (reflection, daydreaming) driven by cron or systemd.
- You only need one module and want to take it on its own.

## 📋 Requirements

- Python 3 (CI runs 3.11); the scripts use only the standard library.
- Optional: the [`gh`](https://cli.github.com/) CLI — only needed for topic-lab planting and for labelling escalations.
- Optional: an OpenAI-compatible or Anthropic-compatible LLM API — only needed by meditation and daydream. Configure it with `LLM_API_BASE`, `LLM_API_KEY`, `LLM_MODEL` and `LLM_API_TYPE` (see [skill-meditation](skill-meditation/README.md)).

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/ythx-101/six6.git
cd six6

# 2. Install: creates the base dir and copies scheduling templates into it
bash distribution/install.sh --base-dir ~/agent

# 3. Validate the protocol files
python3 runtime/scripts/six6.py validate --base-dir ~/agent

# 4. Fire a heartbeat pulse
python3 runtime/scripts/six6.py pulse heartbeat --base-dir ~/agent
```

Then schedule the pulses with [`distribution/templates/cron.example`](distribution/templates/cron.example) (a copy is placed in `~/agent/examples/`) or [`distribution/templates/systemd.example`](distribution/templates/systemd.example). Use `python3 runtime/scripts/six6.py doctor --base-dir ~/agent` for a health check.

### Try the demo

```bash
python3 runtime/scripts/six6.py validate --base-dir demo
python3 runtime/scripts/six6.py pulse heartbeat --base-dir demo
```

Note: some demo commands (such as `doctor` or `farm.py --add-water`) write run files into `demo/`. See [demo/README.md](demo/README.md).

## 🔁 Usage example

A full loop: remember → reflect → daydream → grow ideas.

```bash
BASE=~/agent
python3 skill-memory/scripts/remember.py "Read a paper on agent memory" --base-dir $BASE
python3 skill-memory/scripts/update_now.py "Drafting a post about file-based memory" --base-dir $BASE
# needs LLM_API_KEY:
python3 runtime/scripts/six6.py pulse nightly --base-dir $BASE   # meditation -> MEMORY.md
python3 runtime/scripts/six6.py pulse idle --base-dir $BASE      # daydream -> new seed
python3 runtime/scripts/six6.py pulse daily --base-dir $BASE     # topic-lab tick
python3 skill-topic-lab/scripts/farm.py --add-water <seed-id> --base-dir $BASE
```

The base directory created by `six6.py init` looks like this:

```
~/agent/
├── NOW.md                      # short-term context
├── MEMORY.md                   # long-term core memory
├── memory/                     # daily episodic notes (YYYY-MM-DD.md)
├── data/
│   ├── inbox.jsonl             # task / event queue
│   ├── topic-lab-seeds.jsonl   # idea seeds
│   ├── evolution.md            # meditation output log
│   └── health.json             # written by `six6.py doctor`
└── deadletter/                 # failed inbox items
```

## 🆚 Comparison

A qualitative comparison of approaches (not a benchmark):

| | six6 | Vector-database memory layer | All-in-one agent framework |
|---|---|---|---|
| Storage | Markdown + JSONL files | Embeddings in a vector store | Framework-specific |
| Human-readable / git-diffable | Yes | Generally no | Varies |
| Third-party dependencies | None (stdlib only) | Typically a database and client libraries | Typically many |
| Modules usable on their own | Yes, they do not import each other | Varies | Usually tied together |
| Semantic (embedding) search | **No** | Yes | Varies |

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
   - Tracks maturity. When a seed reaches maturity ≥ 80 on a daily tick, it automatically triggers external outputs (e.g., creating a GitHub Issue).

5. **`skill-autoloop` (Action Center)**
   - The task queuing and execution hub.
   - Manages `inbox.jsonl` and handles escalation protocols (e.g., `needs-decision`).

6. **`skill-monitor` (Life Support / Heartbeat)**
   - The chronometer and health checker. Manages system pulses and triggers for the other modules.

## ❓ FAQ

**What is six6? (six6 是什么？)**
A file-based memory and cognition toolkit for AI agents: six decoupled Python modules that share state only through Markdown and JSONL files.

**Does six6 need a vector database?**
No. Everything is stored as Markdown and JSONL. (six6 does not provide semantic search.)

**Which LLMs does it work with?**
Meditation and daydream work with any OpenAI-compatible `/chat/completions` endpoint or Anthropic-compatible `/v1/messages` endpoint; `<think>` blocks are stripped from replies. See [skill-meditation](skill-meditation/README.md) for Ollama and MiniMax examples.

**Can I use only the memory module? (可以只用记忆模块吗？)**
Yes. Modules do not import each other.

**Do I have to use OpenClaw?**
No. The project is packaged for OpenClaw, but the scripts do not depend on it; any agent or cron job that can run Python scripts and read files can use them.

**How do I schedule it?**
Use the cron and systemd templates in [`distribution/templates/`](distribution/templates/).

**What happens when an idea matures?**
On a daily tick, a seed with maturity ≥ 80 becomes a GitHub Issue (label `idea`) via `gh` and is marked `planted`. Without `gh`, planting is skipped.

**How do I migrate from a clawd workspace?**
Run `distribution/migrate_from_clawd.py` (see [distribution/README.md](distribution/README.md)); it only appends/merges.

**Is my data sent anywhere?**
Meditation and daydream send memory text to the LLM endpoint you configure. If `gh` is installed, topic-lab sends a mature seed's topic and description to GitHub as an Issue, and autoloop adds a `needs-decision` label to escalated Issues. Nothing else leaves your machine.

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
