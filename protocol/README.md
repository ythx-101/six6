# six6 Core Protocol

This layer defines the stable contracts shared by all six6 modules.
It exists to preserve the six-module design while making the system portable,
testable, and safe to integrate into different OpenClaw deployments.

## Goals

- Preserve the six-module architecture.
- Make file contracts machine-checkable.
- Keep module coupling at the file-protocol level.

## Canonical Files

- `NOW.md`: short-term working state.
- `MEMORY.md`: long-term consolidated memory.
- `memory/YYYY-MM-DD.md`: append-only daily memory log.
- `data/inbox.jsonl`: central task and event queue.
- `data/topic-lab-seeds.jsonl`: idea seed database.
- `data/health.json`: runtime health heartbeat.
- `data/evolution.md`: meditation evolution log.

## Schemas

- `schemas/inbox-item.schema.json`
- `schemas/topic-lab-seed.schema.json`
- `schemas/health.schema.json`

## Closed Loop

The canonical six6 loop is:

1. `skill-daydream` writes seeds into `topic-lab-seeds.jsonl`.
2. `skill-topic-lab` matures, composts, or plants those seeds.
3. `skill-topic-lab` emits lifecycle events into `inbox.jsonl`.
4. `skill-autoloop` dispatches inbox items and can water a seed by writing back into Topic Lab.

This preserves the original six-module mental model while formalizing the interfaces.
