import os
import json
import argparse
import datetime
import subprocess
import tempfile

def load_seeds(filepath):
    if not os.path.exists(filepath):
        return []
    seeds = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    seeds.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return seeds

def save_seeds(filepath, seeds):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix="seeds-", suffix=".jsonl", dir=os.path.dirname(filepath))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for seed in seeds:
                f.write(json.dumps(seed, ensure_ascii=False) + "\n")
        os.replace(tmp_path, filepath)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def emit_inbox_event(base_dir, payload):
    inbox_path = os.path.join(base_dir, "data", "inbox.jsonl")
    os.makedirs(os.path.dirname(inbox_path), exist_ok=True)
    payload = dict(payload)
    payload.setdefault("type", "topic-lab-event")
    payload.setdefault("source", "skill-topic-lab")
    payload.setdefault("ts", int(datetime.datetime.now().timestamp()))
    with open(inbox_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def plant_seed(seed):
    """Convert a mature seed into a GitHub Issue."""
    title = f"[topic-lab] {seed.get('topic', 'Untitled Seed')}"
    body = f"## 💡 Mature Idea from Topic Lab\n\n**Description:**\n{seed.get('description', '')}\n\n**Source:** {seed.get('source', 'unknown')}\n**Generated:** {seed.get('created_at', 'unknown')}"
    
    print(f"🌱 Planting seed '{title}' to GitHub Issue...")
    try:
        # Assumes `gh` CLI is authenticated and repo is set (or runs in repo context)
        # Using a dry-run style print for the OS skeleton, but executing the command if possible
        cmd = ["gh", "issue", "create", "--title", title, "--body", body, "--label", "idea"]
        if seed.get("repo"):
            cmd.extend(["--repo", seed["repo"]])
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        issue_url = result.stdout.strip()
        print("✅ Issue created successfully.")
        return True, issue_url
    except FileNotFoundError:
        print("⚠️ `gh` CLI not found. Skipping issue creation.")
        return False, ""
    except subprocess.CalledProcessError as e:
        stderr = e.stderr if isinstance(e.stderr, str) else e.stderr.decode("utf-8")
        print(f"❌ Failed to create issue. Error: {stderr}")
        return False, ""

def main():
    parser = argparse.ArgumentParser(description="Run daily maintenance on the Topic Lab (Farm).")
    parser.add_argument("--base-dir", default=".", help="Base directory of the agent.")
    parser.add_argument("--tick", action="store_true", help="Perform daily decay and maturity checks.")
    parser.add_argument("--add-water", type=str, help="Add +10 maturity to a specific seed ID.")
    args = parser.parse_args()

    seeds_file = os.path.join(args.base_dir, "data", "topic-lab-seeds.jsonl")
    seeds = load_seeds(seeds_file)
    
    if not seeds:
        print("🪹 Topic Lab is empty. No seeds to process.")
        return

    updated_seeds = []
    
    if args.add_water:
        for seed in seeds:
            if seed.get("id") == args.add_water and seed.get("status", "active") == "active":
                seed["maturity"] = min(100, seed.get("maturity", 0) + 10)
                seed["last_event"] = "watered"
                print(f"💧 Watered seed '{seed.get('topic')}'. Maturity is now {seed['maturity']}.")
                emit_inbox_event(args.base_dir, {
                    "event": "seed-watered",
                    "seed_id": seed.get("id"),
                    "topic": seed.get("topic"),
                    "status": seed.get("status", "active"),
                })
            updated_seeds.append(seed)
        save_seeds(seeds_file, updated_seeds)
        return

    if args.tick:
        print("⏱️ Running daily tick in Topic Lab...")
        for seed in seeds:
            status = seed.get("status", "active")
            if status != "active":
                updated_seeds.append(seed)
                continue
            
            maturity = seed.get("maturity", 10)
            
            # Check maturity thresholds
            if maturity >= 80:
                success, issue_url = plant_seed(seed)
                if success:
                    seed["status"] = "planted"
                    seed["planted_issue_url"] = issue_url
                    seed["last_event"] = "planted"
                    emit_inbox_event(args.base_dir, {
                        "event": "seed-planted",
                        "seed_id": seed.get("id"),
                        "topic": seed.get("topic"),
                        "status": "planted",
                        "msg": f"Seed planted into GitHub Issue: {seed.get('topic')}",
                    })
            else:
                # Apply decay
                seed["maturity"] = max(0, maturity - 5)
                if seed["maturity"] <= 20:
                    print(f"🍂 Seed '{seed.get('topic')}' withered (composted) due to low maturity.")
                    seed["status"] = "composted"
                    seed["last_event"] = "composted"
                    emit_inbox_event(args.base_dir, {
                        "event": "seed-composted",
                        "seed_id": seed.get("id"),
                        "topic": seed.get("topic"),
                        "status": "composted",
                        "msg": f"Seed composted after decay: {seed.get('topic')}",
                    })
            
            updated_seeds.append(seed)
            
        save_seeds(seeds_file, updated_seeds)
        print("✅ Topic Lab tick complete.")

if __name__ == "__main__":
    main()
