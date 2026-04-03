import os
import re
import json
import urllib.request
import datetime
import argparse

def call_llm(api_base, api_key, model, prompt):
    url = f"{api_base.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Run nightly meditation to consolidate memory.")
    parser.add_argument("--base-dir", default=".", help="Base directory of the agent.")
    parser.add_argument("--date", help="Date of the memory to process (YYYY-MM-DD). Defaults to today.", default=datetime.datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--api-base", default=os.environ.get("LLM_API_BASE", "https://api.openai.com/v1"), help="OpenAI-compatible API Base URL")
    parser.add_argument("--api-key", default=os.environ.get("LLM_API_KEY", ""), help="API Key")
    parser.add_argument("--model", default=os.environ.get("LLM_MODEL", "gpt-4o"), help="Model to use")
    args = parser.parse_args()

    if not args.api_key:
        print("❌ Error: API Key is required. Set LLM_API_KEY env var or use --api-key.")
        return

    mem_path = os.path.join(args.base_dir, "MEMORY.md")
    daily_path = os.path.join(args.base_dir, "memory", f"{args.date}.md")
    evo_path = os.path.join(args.base_dir, "data", "evolution.md")

    if not os.path.exists(daily_path):
        print(f"⚠️ No daily memory found at {daily_path}. Skipping meditation.")
        return

    with open(daily_path, "r", encoding="utf-8") as f:
        daily_memory = f.read()

    core_memory = ""
    if os.path.exists(mem_path):
        with open(mem_path, "r", encoding="utf-8") as f:
            core_memory = f.read()

    prompt = f"""You are the core cognition of an AI Agent. It is time for your nightly meditation.
Your current long-term memory:
<core_memory>
{core_memory}
</core_memory>

Today's episodic memory:
<daily_memory>
{daily_memory}
</daily_memory>

Task:
1. Synthesize today's events with your long-term memory. 
2. Output a revised long-term memory wrapped in <new_memory> tags. Keep it concise, structured, and insightful.
3. Output a brief 1-sentence reflection on how you evolved today wrapped in <evolution> tags.
"""

    print(f"🧘 Initiating meditation for {args.date} using {args.model}...")
    response = call_llm(args.api_base, args.api_key, args.model, prompt)
    if not response:
        return

    new_memory_match = re.search(r"<new_memory>\n?(.*?)\n?</new_memory>", response, re.DOTALL)
    evo_match = re.search(r"<evolution>\n?(.*?)\n?</evolution>", response, re.DOTALL)

    if new_memory_match:
        with open(mem_path, "w", encoding="utf-8") as f:
            f.write(new_memory_match.group(1).strip())
        print(f"✅ Core MEMORY.md updated.")
    
    if evo_match:
        os.makedirs(os.path.dirname(evo_path), exist_ok=True)
        evo_text = evo_match.group(1).strip()
        with open(evo_path, "a", encoding="utf-8") as f:
            f.write(f"- **{args.date}**: {evo_text}\n")
        print(f"🌱 Evolution log appended: {evo_text}")

if __name__ == "__main__":
    main()
