import os
import sys
import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description="Append a memory to today's journal.")
    parser.add_argument("text", help="The memory content to store.")
    parser.add_argument("--base-dir", default=".", help="Base directory containing the memory/ folder.")
    args = parser.parse_args()

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    mem_dir = os.path.join(args.base_dir, "memory")
    os.makedirs(mem_dir, exist_ok=True)
    file_path = os.path.join(mem_dir, f"{today}.md")

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"- **[{timestamp}]** {args.text}\n"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"✅ Memory saved to {file_path}")

if __name__ == "__main__":
    main()
