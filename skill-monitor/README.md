# 🫀 skill-monitor (Life Support / Heartbeat)

The pacing mechanism of the Organic OS. While the other 5 modules define *what* the Agent can do, `skill-monitor` defines *when* they do it. It acts as a standardized entry point for standard OS crontabs or agent loop triggers to breathe life into the system.

## Data Flow
- **Outputs**: Executes the scripts of the other 5 modules using `subprocess`.

## The Pulse Types

The system responds to 4 standard "pulses":
1. **`heartbeat`**: Frequent (e.g., every 5 minutes). Flushes `skill-autoloop` (the inbox).
2. **`daily`**: Once a day. Triggers `skill-topic-lab` to decay or harvest ideas.
3. **`nightly`**: Once a night. Triggers `skill-meditation` to consolidate episodic memory into core memory.
4. **`idle`**: Triggered randomly. Triggers `skill-daydream` to generate serendipitous seeds.

## Usage

You should map these commands to your host machine's `crontab` or your orchestrator's equivalent:

```bash
# Frequent heartbeat
python3 scripts/pulse.py heartbeat

# Daily tick
python3 scripts/pulse.py daily

# Nightly reflection
python3 scripts/pulse.py nightly

# Random daydreaming
python3 scripts/pulse.py idle
```

### Example Linux Crontab Setup
```crontab
*/5 * * * * /usr/bin/python3 /path/to/six6/skill-monitor/scripts/pulse.py heartbeat >> /tmp/agent_heartbeat.log 2>&1
0 10 * * *  /usr/bin/python3 /path/to/six6/skill-monitor/scripts/pulse.py daily
0 2 * * *   /usr/bin/python3 /path/to/six6/skill-monitor/scripts/pulse.py nightly
0 14 * * 0  /usr/bin/python3 /path/to/six6/skill-monitor/scripts/pulse.py idle
```
