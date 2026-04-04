# six6 Distribution

This layer is for packaging six6 as an installable OpenClaw skill set.

## Purpose

- Keep the six cognitive modules as the primary user-facing abstraction.
- Add install, migration, and operator-facing docs without polluting module logic.
- Make it obvious how to wire six6 into an existing OpenClaw workspace.

## Files

- `SKILL.md`: when to use this layer and concrete commands.
- `install.sh`: idempotent installer. Run once per target machine.
- `templates/cron.example`: crontab fragment for scheduling six6 pulses.
- `templates/systemd.example`: systemd service and timer examples for scheduled pulses.
- `migrate_from_clawd.py`: migrates an existing clawd workspace into a six6 base dir.

## Quick Start

### Install

  bash distribution/install.sh --base-dir /path/to/agent/root

  Optionally override the repo root (defaults to the parent of distribution/):
  bash distribution/install.sh --base-dir /path/to/agent/root --six6-dir /path/to/six6

### Validate

  python3 runtime/scripts/six6.py validate --base-dir /path/to/agent/root

### Health check

  python3 runtime/scripts/six6.py doctor --base-dir /path/to/agent/root

### Heartbeat pulse

  python3 runtime/scripts/six6.py pulse heartbeat --base-dir /path/to/agent/root

### Migrate from clawd

  python3 distribution/migrate_from_clawd.py \
    --source-dir /path/to/clawd/workspace \
    --base-dir   /path/to/agent/root

  Files migrated (append/merge only, never destructive):
    NOW.md, MEMORY.md           - appended if content not already present
    memory/YYYY-MM-DD.md        - each daily file appended individually
    data/inbox.jsonl            - new lines merged by deduplication
    data/topic-lab-seeds.jsonl  - new lines merged by deduplication

## Notes

- install.sh is idempotent: safe to run multiple times.
- install.sh copies cron.example and systemd.example into <base-dir>/examples/.
- migrate_from_clawd.py appends/merges; it never overwrites existing data destructively.
- All paths are configurable via flags. No private paths are hardcoded anywhere.
