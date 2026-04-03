# ☁️ skill-daydream (Divergent Ideation)

This module provides the Agent with a serendipitous ideation mechanism. It randomly activates during idle times (scheduled via `skill-monitor`) to cross-pollinate disjointed memory fragments and generate novel ideas.

## Data Flow
- **Inputs**: Randomly samples files from `memory/*.md` (managed by `skill-memory`).
- **Outputs**: Appends new idea seeds as JSON objects to `data/topic-lab-seeds.jsonl`.

## Concept

Instead of linear task execution, `skill-daydream` introduces *mutation* into the Agent's thought process. By reading random historical logs, the LLM is prompted with a high-temperature setting to find non-obvious connections.

The resulting "seeds" start with a base `maturity` of `10` and are handed off to the `skill-topic-lab` for nurturing or eventual pruning.

## Usage

```bash
export LLM_API_BASE="https://api.openai.com/v1"
export LLM_API_KEY="sk-..."
export LLM_MODEL="gpt-4o"

python3 scripts/daydream.py --base-dir /path/to/agent/root
```

### Absolute Decoupling Standard
The JSON object written to `topic-lab-seeds.jsonl` follows this exact schema:
```json
{
  "id": "dd-a1b2c3d4",
  "topic": "String",
  "description": "String",
  "source": "skill-daydream",
  "maturity": 10,
  "created_at": "ISO-8601 Timestamp"
}
```
Any other module in the `six6` ecosystem can safely read or append to this file.
