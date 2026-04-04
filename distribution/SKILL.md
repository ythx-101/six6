# six6 Distribution Layer

## When to Use This Layer

Use the distribution layer when you want to:

- Install six6 into an existing OpenClaw workspace for the first time.
- Migrate an existing clawd-based agent to six6.
- Wire six6 into a cron or systemd schedule on a server.
- Package six6 as a redistributable OpenClaw skill set.

You do NOT need this layer if you are only developing or extending individual modules.
The six modules under skill-* are self-contained and can be used independently.

## Files in This Layer

- `install.sh`: idempotent installer. Initializes a base dir and copies examples.
- `templates/cron.example`: drop-in crontab fragment for scheduling six6 pulses.
- `templates/systemd.example`: systemd service and timer examples for scheduled pulses.
- `migrate_from_clawd.py`: migrates an existing clawd workspace into a six6 base dir.

## Concrete Commands

### Install

  bash distribution/install.sh --base-dir /path/to/agent/root --six6-dir /path/to/six6

### Validate after install

  python3 runtime/scripts/six6.py validate --base-dir /path/to/agent/root

### Run a health check

  python3 runtime/scripts/six6.py doctor --base-dir /path/to/agent/root

### Fire a manual heartbeat pulse

  python3 runtime/scripts/six6.py pulse heartbeat --base-dir /path/to/agent/root

### Migrate from clawd

  python3 distribution/migrate_from_clawd.py \
    --source-dir /path/to/clawd/workspace \
    --base-dir   /path/to/agent/root

## Notes

- All paths are configurable. No private paths are hardcoded.
- install.sh is idempotent: running it twice will not overwrite existing data files.
- migrate_from_clawd.py appends rather than overwrites when merging memory and JSONL files.
