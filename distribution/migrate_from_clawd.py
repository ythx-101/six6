#!/usr/bin/env python3
"""migrate_from_clawd.py - Migrate a clawd workspace into a six6 base dir.

Usage:
  python3 distribution/migrate_from_clawd.py \
    --source-dir /path/to/clawd/workspace \
    --base-dir   /path/to/six6/agent/root
"""
import argparse
import glob
import os
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def append_text(dst, content, separator="\n\n---\n\n"):
    """Append content to dst, creating it if absent. Never overwrites."""
    if os.path.exists(dst):
        existing = read_text(dst)
        if content.strip() in existing:
            return False  # already present
        with open(dst, "a", encoding="utf-8") as f:
            f.write(separator + content)
    else:
        parent = os.path.dirname(dst)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
    return True


def merge_jsonl(src, dst):
    """Append lines from src that are not already in dst."""
    if not os.path.exists(src):
        return 0
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    existing_lines = set()
    if os.path.exists(dst):
        with open(dst, "r", encoding="utf-8") as f:
            existing_lines = {l.strip() for l in f if l.strip()}
    added = 0
    with open(src, "r", encoding="utf-8") as src_f, \
         open(dst, "a", encoding="utf-8") as dst_f:
        for line in src_f:
            stripped = line.strip()
            if stripped and stripped not in existing_lines:
                dst_f.write(stripped + "\n")
                existing_lines.add(stripped)
                added += 1
    return added


def main():
    parser = argparse.ArgumentParser(description="Migrate clawd workspace to six6")
    parser.add_argument("--source-dir", required=True, help="Path to clawd workspace root")
    parser.add_argument("--base-dir",   required=True, help="Path to six6 agent base dir")
    args = parser.parse_args()

    src = os.path.abspath(args.source_dir)
    dst = os.path.abspath(args.base_dir)

    if not os.path.isdir(src):
        print(f"Error: --source-dir does not exist: {src}", file=sys.stderr)
        sys.exit(1)

    summary = []

    # --- NOW.md ---
    src_now = os.path.join(src, "NOW.md")
    if os.path.exists(src_now):
        dst_now = os.path.join(dst, "NOW.md")
        changed = append_text(dst_now, read_text(src_now))
        summary.append(f"NOW.md: {'appended' if changed else 'skipped (already present)'}")
    else:
        summary.append("NOW.md: not found in source, skipped")

    # --- MEMORY.md ---
    src_mem = os.path.join(src, "MEMORY.md")
    if os.path.exists(src_mem):
        dst_mem = os.path.join(dst, "MEMORY.md")
        changed = append_text(dst_mem, read_text(src_mem))
        summary.append(f"MEMORY.md: {'appended' if changed else 'skipped (already present)'}")
    else:
        summary.append("MEMORY.md: not found in source, skipped")

    # --- Daily memory files (memory/YYYY-MM-DD.md) ---
    daily_files = sorted(glob.glob(os.path.join(src, "memory", "*.md")))
    daily_added = 0
    daily_skipped = 0
    for daily_src in daily_files:
        fname = os.path.basename(daily_src)
        daily_dst = os.path.join(dst, "memory", fname)
        changed = append_text(daily_dst, read_text(daily_src))
        if changed:
            daily_added += 1
        else:
            daily_skipped += 1
    summary.append(f"Daily memory files: {daily_added} appended, {daily_skipped} skipped")

    # --- inbox.jsonl ---
    src_inbox = os.path.join(src, "data", "inbox.jsonl")
    dst_inbox = os.path.join(dst, "data", "inbox.jsonl")
    n = merge_jsonl(src_inbox, dst_inbox)
    summary.append(f"inbox.jsonl: {n} lines merged" if os.path.exists(src_inbox) else "inbox.jsonl: not found in source, skipped")

    # --- topic-lab-seeds.jsonl ---
    src_seeds = os.path.join(src, "data", "topic-lab-seeds.jsonl")
    dst_seeds = os.path.join(dst, "data", "topic-lab-seeds.jsonl")
    n = merge_jsonl(src_seeds, dst_seeds)
    summary.append(f"topic-lab-seeds.jsonl: {n} lines merged" if os.path.exists(src_seeds) else "topic-lab-seeds.jsonl: not found in source, skipped")

    print("\n=== Migration Summary ===")
    for line in summary:
        print(f"  {line}")
    print("========================\n")


if __name__ == "__main__":
    main()
