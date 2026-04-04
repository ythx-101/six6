# six6 Demo Base Dir

This directory is a minimal example of a writable six6 agent base directory.

It exists so a new user can inspect the expected file layout before wiring six6
into a real OpenClaw workspace.

## Contents

- `NOW.md`: current working context.
- `MEMORY.md`: long-term summary.
- `memory/`: daily append-only memory files.
- `data/inbox.jsonl`: empty inbox queue.
- `data/topic-lab-seeds.jsonl`: one sample seed.
- `data/evolution.md`: meditation output log.

## Try It

From the repository root:

```bash
python3 runtime/scripts/six6.py validate --base-dir demo
python3 runtime/scripts/six6.py doctor --base-dir demo
python3 runtime/scripts/six6.py pulse heartbeat --base-dir demo
python3 skill-topic-lab/scripts/farm.py --base-dir demo --add-water demo-seed-1
```

The demo uses only local files. It does not require GitHub writes unless you
manually raise seed maturity high enough and run a planting tick.
