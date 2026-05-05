# ☁️ skill-daydream (Divergent Ideation)

This module provides the Agent with a serendipitous ideation mechanism. It randomly activates during idle times (scheduled via `skill-monitor`) to cross-pollinate disjointed memory fragments and generate novel ideas.

## Data Flow
- **Inputs**: Randomly samples files from `memory/*.md` (managed by `skill-memory`).
- **Outputs**: Appends new idea seeds as JSON objects to `data/topic-lab-seeds.jsonl`.

## Concept

Instead of linear task execution, `skill-daydream` introduces *mutation* into the Agent's thought process. By reading random historical logs, the LLM is prompted with a configurable high-temperature setting (default `0.8`) to find non-obvious connections.

*Note: The script automatically filters out `<think>...</think>` chain-of-thought blocks, making it highly compatible with reasoning models (like DeepSeek or MiniMax) without breaking the JSON output schema.*

The resulting "seeds" start with a base `maturity` of `30` so they survive at least one farm review before being nurtured or pruned.

## Usage

```bash
# Standard OpenAI Configuration
export LLM_API_BASE="https://api.openai.com/v1"
export LLM_API_KEY="sk-..."
export LLM_MODEL="gpt-4o"

# Optional: Multi-Provider & Generation Settings
export LLM_API_TYPE="openai"       # Set to "anthropic" for Claude/MiniMax Anthropic endpoints (Auto-detected from API Base)
export DAYDREAM_TEMPERATURE="0.8"  # Adjust creativity (0.6 - 1.2+ for divergent thinking)

python3 scripts/daydream.py --base-dir /path/to/agent/root
```

> [!IMPORTANT]
> **Configuration Strictness**
> Please configure the environment variables exactly as shown in the examples above:
> - **`LLM_API_BASE`**: Pay attention to the trailing path. For OpenAI, include `/v1` (the script appends `/chat/completions`). For Anthropic-compatible endpoints, do **not** include `/v1` (the script automatically appends `/v1/messages`), otherwise it will result in a malformed double `/v1/v1/` URL.
> - **`LLM_API_TYPE`**: If set manually, it must be strict lowercase (`openai` or `anthropic`).
> - **`DAYDREAM_TEMPERATURE`**: Must be a valid float string (e.g., `0.8`).

### Absolute Decoupling Standard
The JSON object written to `topic-lab-seeds.jsonl` follows this exact schema:
```json
{
  "id": "dd-a1b2c3d4",
  "topic": "String",
  "description": "String",
  "source": "skill-daydream",
  "maturity": 30,
  "created_at": "ISO-8601 Timestamp"
}
```
Any other module in the `six6` ecosystem can safely read or append to this file.
