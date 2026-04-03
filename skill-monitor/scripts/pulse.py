import os
import argparse
import subprocess
import datetime
import sys

def run_module_script(base_dir, module, script_name, extra_args=None):
    script_path = os.path.join(base_dir, module, "scripts", script_name)
    if not os.path.exists(script_path):
        print(f"⚠️ Warning: Script {script_path} not found. Skipping.")
        return False
    
    cmd = [sys.executable, script_path, "--base-dir", os.path.dirname(os.path.abspath(base_dir))]
    if extra_args:
        cmd.extend(extra_args)
        
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🫀 Pulse triggering: {module}/{script_name}")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {module}/{script_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="The Heartbeat/Pulse of the Organic OS.")
    parser.add_argument("--base-dir", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), help="Base directory of the six6 modules.")
    parser.add_argument("pulse_type", choices=["heartbeat", "daily", "nightly", "idle"], help="Type of pulse to trigger.")
    args = parser.parse_args()

    pulse = args.pulse_type
    six6_dir = args.base_dir

    print(f"=== 💓 Initiating {pulse.upper()} pulse ===")

    if pulse == "heartbeat":
        # Frequent check (e.g., every 5-10 minutes)
        # 1. Process Inbox
        run_module_script(six6_dir, "skill-autoloop", "process_inbox.py")
        
    elif pulse == "daily":
        # Runs once a day (e.g., 10:00 AM)
        # 1. Farm/Topic Lab maintenance
        run_module_script(six6_dir, "skill-topic-lab", "farm.py", ["--tick"])
        
    elif pulse == "nightly":
        # Runs once at night (e.g., 02:00 AM)
        # 1. Meditate and consolidate memory
        run_module_script(six6_dir, "skill-meditation", "meditate.py")
        
    elif pulse == "idle":
        # Runs randomly when system load is low
        # 1. Daydream
        run_module_script(six6_dir, "skill-daydream", "daydream.py")

    print(f"=== 💓 {pulse.upper()} pulse complete ===")

if __name__ == "__main__":
    main()
