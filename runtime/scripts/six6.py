#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import subprocess
import sys


MODULES = [
    "skill-memory",
    "skill-meditation",
    "skill-daydream",
    "skill-topic-lab",
    "skill-autoloop",
    "skill-monitor",
]


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_jsonl(path):
    items = []
    if not os.path.exists(path):
        return items
    with open(path, "r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                items.append((line_no, json.loads(raw)))
            except json.JSONDecodeError as exc:
                items.append((line_no, {"__invalid__": str(exc), "__raw__": raw}))
    return items


def ensure_file(path, default_content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(default_content)


def init_base_dir(base_dir):
    ensure_file(os.path.join(base_dir, "NOW.md"), "# NOW (Current Context)\n\n")
    ensure_file(os.path.join(base_dir, "MEMORY.md"), "# MEMORY\n\n")
    ensure_file(os.path.join(base_dir, "data", "inbox.jsonl"))
    ensure_file(os.path.join(base_dir, "data", "topic-lab-seeds.jsonl"))
    ensure_file(os.path.join(base_dir, "data", "evolution.md"))
    os.makedirs(os.path.join(base_dir, "memory"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "deadletter"), exist_ok=True)
    print(f"Initialized six6 base dir at {base_dir}")


def validate_inbox_item(item):
    if "__invalid__" in item:
        return False, item["__invalid__"]
    if not isinstance(item.get("type"), str) or not item["type"]:
        return False, "missing non-empty 'type'"
    if not isinstance(item.get("ts"), int):
        return False, "missing integer 'ts'"
    return True, ""


def validate_seed(item):
    if "__invalid__" in item:
        return False, item["__invalid__"]
    required = ["id", "topic", "description", "source", "maturity", "created_at"]
    for key in required:
        if key not in item:
            return False, f"missing '{key}'"
    if not isinstance(item["maturity"], int) or item["maturity"] < 0 or item["maturity"] > 100:
        return False, "invalid 'maturity'"
    return True, ""


def validate_base_dir(base_dir):
    inbox_path = os.path.join(base_dir, "data", "inbox.jsonl")
    seeds_path = os.path.join(base_dir, "data", "topic-lab-seeds.jsonl")
    issues = []

    for line_no, item in load_jsonl(inbox_path):
        ok, reason = validate_inbox_item(item)
        if not ok:
            issues.append(f"inbox.jsonl:{line_no}: {reason}")

    for line_no, item in load_jsonl(seeds_path):
        ok, reason = validate_seed(item)
        if not ok:
            issues.append(f"topic-lab-seeds.jsonl:{line_no}: {reason}")

    if issues:
        print("Validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Validation passed.")
    return 0


def doctor(base_dir):
    checks = []
    checks.append(("base_dir_exists", os.path.isdir(base_dir)))
    checks.append(("memory_dir_exists", os.path.isdir(os.path.join(base_dir, "memory"))))
    checks.append(("data_dir_exists", os.path.isdir(os.path.join(base_dir, "data"))))
    checks.append(("gh_available", subprocess.run(["which", "gh"], capture_output=True).returncode == 0))

    status = "ok" if all(result for _, result in checks) else "warn"

    modules = {}
    six6_root = repo_root()
    for module in MODULES:
        modules[module] = os.path.isdir(os.path.join(six6_root, module))

    payload = {
        "updated_at": datetime.datetime.now().isoformat(),
        "status": status,
        "base_dir": base_dir,
        "checks": {name: result for name, result in checks},
        "modules": modules,
    }

    health_path = os.path.join(base_dir, "data", "health.json")
    os.makedirs(os.path.dirname(health_path), exist_ok=True)
    with open(health_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "ok" else 1


def pulse(command_base_dir, pulse_type):
    script = os.path.join(repo_root(), "skill-monitor", "scripts", "pulse.py")
    cmd = [sys.executable, script, "--base-dir", command_base_dir, pulse_type]
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(description="six6 runtime entrypoint")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--base-dir", default=repo_root())

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--base-dir", default=repo_root())

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--base-dir", default=repo_root())

    pulse_parser = subparsers.add_parser("pulse")
    pulse_parser.add_argument("pulse_type", choices=["heartbeat", "daily", "nightly", "idle"])
    pulse_parser.add_argument("--base-dir", default=repo_root())

    args = parser.parse_args()

    if args.command == "init":
        init_base_dir(os.path.abspath(args.base_dir))
        return
    if args.command == "validate":
        raise SystemExit(validate_base_dir(os.path.abspath(args.base_dir)))
    if args.command == "doctor":
        raise SystemExit(doctor(os.path.abspath(args.base_dir)))
    if args.command == "pulse":
        raise SystemExit(pulse(os.path.abspath(args.base_dir), args.pulse_type))


if __name__ == "__main__":
    main()
