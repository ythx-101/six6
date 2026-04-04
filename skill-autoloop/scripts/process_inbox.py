import os
import json
import argparse
import subprocess
import datetime
import tempfile


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def append_deadletter(base_dir, item, reason):
    deadletter_dir = os.path.join(base_dir, "deadletter")
    os.makedirs(deadletter_dir, exist_ok=True)
    deadletter_file = os.path.join(deadletter_dir, "inbox-deadletter.jsonl")
    payload = {
        "failed_at": datetime.datetime.now().isoformat(),
        "reason": reason,
        "item": item,
    }
    with open(deadletter_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def load_inbox(filepath):
    if not os.path.exists(filepath):
        return []
    items = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return items

def save_inbox(filepath, items):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix="inbox-", suffix=".jsonl", dir=os.path.dirname(filepath))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        os.replace(tmp_path, filepath)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def dispatch_task(base_dir, item):
    """
    Dummy dispatcher. In a real environment, this would call standard sub-agent scripts 
    (e.g., cc-task.sh or auto-fixer) depending on the task type.
    """
    task_type = item.get("type", "generic")
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Dispatching task type: {task_type}")
    
    if task_type == "escalation":
        issue_num = item.get("issue_number")
        print(f"🚨 Escalation caught for Issue #{issue_num}. Reason: {item.get('reason')}")
        print("-> Action: Marking with 'needs-decision' for Main Agent (Cerebral Cortex) to handle.")
        try:
            cmd = ["gh", "issue", "edit", str(issue_num), "--add-label", "needs-decision"]
            repo = item.get("repo")
            if repo:
                cmd.extend(["--repo", repo])
            subprocess.run(cmd, check=True, capture_output=True)
        except Exception:
            print("   (gh CLI not available, skipped label update)")
        return True

    elif task_type == "x-todo":
        print(f"📝 External Todo received: {item.get('msg')}")
        print("-> Action: Dispatching to sub-agent worker queue...")
        return True

    elif task_type == "topic-lab-water":
        seed_id = item.get("seed_id")
        if not seed_id:
            raise ValueError("topic-lab-water is missing seed_id")
        farm_script = os.path.join(repo_root(), "skill-topic-lab", "scripts", "farm.py")
        cmd = [os.environ.get("PYTHON", "python3"), farm_script, "--base-dir", base_dir, "--add-water", seed_id]
        subprocess.run(cmd, check=True)
        print(f"💧 Routed watering task back to Topic Lab for seed {seed_id}.")
        return True

    else:
        print(f"📥 Generic inbox item: {item.get('msg', str(item))}")
        return True

def main():
    parser = argparse.ArgumentParser(description="Process the Agent's central inbox.")
    parser.add_argument("--base-dir", default=".", help="Base directory of the agent.")
    args = parser.parse_args()

    inbox_file = os.path.join(args.base_dir, "data", "inbox.jsonl")
    items = load_inbox(inbox_file)
    
    if not items:
        print("📭 Inbox is empty. Nothing to process.")
        return

    print(f"📬 Found {len(items)} items in inbox. Processing...")

    remaining_items = []
    for item in items:
        try:
            dispatch_task(args.base_dir, item)
        except Exception as exc:
            append_deadletter(args.base_dir, item, str(exc))
            remaining_items.append(item)
            print(f"❌ Failed to dispatch item: {exc}")
        print("-" * 40)

    save_inbox(inbox_file, remaining_items)
    if remaining_items:
        print(f"⚠️ Inbox processing complete with {len(remaining_items)} failed item(s) retained.")
    else:
        print("✅ Inbox cleared.")

if __name__ == "__main__":
    main()
