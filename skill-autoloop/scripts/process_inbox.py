import os
import json
import argparse
import subprocess
import datetime

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

def clear_inbox(filepath):
    # Empty the inbox after successful processing
    open(filepath, "w").close()

def dispatch_task(item):
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
            subprocess.run(["gh", "issue", "edit", str(issue_num), "--add-label", "needs-decision"], check=True, capture_output=True)
        except Exception:
            print("   (gh CLI not available, skipped label update)")
            
    elif task_type == "x-todo":
        print(f"📝 External Todo received: {item.get('msg')}")
        print("-> Action: Dispatching to sub-agent worker queue...")
        
    else:
        print(f"📥 Generic inbox item: {item.get('msg', str(item))}")

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
    
    for item in items:
        dispatch_task(item)
        print("-" * 40)
        
    clear_inbox(inbox_file)
    print("✅ Inbox cleared.")

if __name__ == "__main__":
    main()
