# six6 Architecture

This document defines the standard data flow and file system conventions for the 6 core six6 modules.
Each module operates independently and communicates strictly via these file standards, achieving absolute decoupling.

The repository also separates concerns into three supporting layers without changing the six-module model:

- `protocol/`: the stable file and schema contracts.
- `runtime/`: the operational CLI and health tooling.
- `distribution/`: packaging and migration guidance for OpenClaw users.

## 1. skill-memory (脑皮层)
- **Role**: Manages short-term and long-term memory.
- **Data Flow**:
  - `NOW.md`: Short-term context, updated on state changes.
  - `memory/YYYY-MM-DD.md`: Daily append-only log of events and thoughts.
  - `MEMORY.md`: Core cognitive summary.

## 2. skill-meditation (反思收敛)
- **Role**: Deep reflection and synthesis.
- **Data Flow**:
  - **Inputs**: Reads `memory/YYYY-MM-DD.md` (nightly).
  - **Outputs**: Synthesizes and updates `MEMORY.md`. Appends to an evolution log.

## 3. skill-daydream (发散变异)
- **Role**: Idea generation and serendipity.
- **Data Flow**:
  - **Inputs**: Randomly samples historical files from `memory/`.
  - **Outputs**: Writes generated ideas as JSON objects to `data/topic-lab-seeds.jsonl`.

## 4. skill-topic-lab (农场/温室)
- **Role**: Manages the lifecycle of ideas/seeds.
- **Data Flow**:
  - **Inputs**: Reads `data/topic-lab-seeds.jsonl`.
  - **Outputs**: Updates maturity scores in a structured JSON schema. When a seed hits >80% maturity, it executes GitHub API to open an Issue and moves the seed to a `planted` state.
  - **Closed Loop**: Emits lifecycle events into `data/inbox.jsonl` so `skill-autoloop` can react.

## 5. skill-autoloop (行动中枢)
- **Role**: Task queuing and escalation management.
- **Data Flow**:
  - **Inputs**: `data/inbox.jsonl` for incoming tasks.
  - **Outputs**: Processes tasks, outputs results or escalates via the `needs-decision` label on GitHub Issues.
  - **Closed Loop**: Accepts `topic-lab-water` tasks and can write back into Topic Lab by invoking `skill-topic-lab`.

## 6. skill-monitor (维生系统/心跳)
- **Role**: Scheduling, health checks, and heartbeat triggers.
- **Data Flow**:
  - **Outputs**: Triggers Cron-based execution scripts for other modules. Logs health status to `data/health.json`.

## Runtime Contracts

- `runtime/scripts/six6.py init` creates the canonical writable directories.
- `runtime/scripts/six6.py validate` checks inbox and seed files against the protocol contracts.
- `runtime/scripts/six6.py doctor` writes `data/health.json`.

---
*Absolute Decoupling Rule: Modules MUST NOT import each other's code. All state transition and communication is via the files listed above.*
