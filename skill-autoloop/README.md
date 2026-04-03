# ⚙️ skill-autoloop (Action Center)

The central nervous system for task queuing and dispatching. Any external trigger (like a cron job finding a new tweet, an error in a sub-agent, or a new GitHub issue) writes a standardized JSON object to `data/inbox.jsonl`.

The Autoloop module then reads this inbox, decides who should handle it (sub-agent worker vs. main brain), and dispatches the action.

## Data Flow
- **Inputs**: `data/inbox.jsonl` (Written to by *any* other script/system).
- **Outputs**: Clears `inbox.jsonl` after processing. Triggers external scripts (e.g., `cc-task.sh`) or escalates to GitHub Issues via the `needs-decision` label.

## Inbox JSON Standard

Any system wanting the agent to "do something" must append a JSON line to `data/inbox.jsonl`:

```json
{"type": "x-todo", "msg": "Read the new paper on LLM memory", "ts": 1712134500}
{"type": "escalation", "issue_number": 89, "reason": "API Key Expired"}
```

## Usage

```bash
python3 scripts/process_inbox.py --base-dir /path/to/agent/root
```

This script is typically run periodically by `skill-monitor`. It prevents the main LLM session from being constantly interrupted, acting as an asynchronous buffer.
