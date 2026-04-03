import os
import argparse
import datetime

def main():
    parser = argparse.ArgumentParser(description="Update the NOW.md short-term context.")
    parser.add_argument("text", help="The new context/task to write.")
    parser.add_argument("--base-dir", default=".", help="Base directory.")
    args = parser.parse_args()

    file_path = os.path.join(args.base_dir, "NOW.md")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"# NOW (Current Context)\n\n*Last updated: {timestamp}*\n\n{args.text}\n"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ NOW.md updated at {file_path}")

if __name__ == "__main__":
    main()
