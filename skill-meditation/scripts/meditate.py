import os
import re
import json
import urllib.error
import urllib.request
import datetime
import argparse


def _response_snippet(error):
    try:
        body = error.read().decode("utf-8", errors="replace")
    except Exception:
        return ""
    body = re.sub(r'("(?:api[_-]?key|token|secret|authorization)"\s*:\s*")[^"\n]+', r'\1***', body, flags=re.IGNORECASE)
    return body[:500]


def call_llm(api_base, api_key, model, prompt, api_type=None, temperature=0.3, retries=2):
    if not api_type:
        api_type = "anthropic" if "anthropic" in api_base.lower() else "openai"

    if api_type == "anthropic":
        url = f"{api_base.rstrip('/')}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": float(temperature),
        }
    else:
        url = f"{api_base.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(temperature),
        }

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    attempts = max(1, int(retries) + 1)
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                if api_type == "anthropic":
                    if "content" not in result:
                        print(f"Unexpected response structure keys: {sorted(result.keys())}")
                        return None
                    content = "".join(c["text"] for c in result["content"] if c.get("type") == "text")
                else:
                    if "choices" not in result or not result["choices"]:
                        print(f"Unexpected response structure keys: {sorted(result.keys())}")
                        return None
                    content = result["choices"][0]["message"]["content"]

                if content:
                    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
                return content
        except urllib.error.HTTPError as exc:
            print(f"HTTPError calling LLM ({api_type}) attempt {attempt}/{attempts}: status={exc.code} reason={exc.reason}")
            snippet = _response_snippet(exc)
            if snippet:
                print(f"Response snippet: {snippet}")
        except Exception as exc:
            print(f"Error calling LLM ({api_type}) attempt {attempt}/{attempts}: {type(exc).__name__}: {exc}")

    return None

def main():
    parser = argparse.ArgumentParser(description="Run nightly meditation to consolidate memory.")
    parser.add_argument("--base-dir", default=".", help="Base directory of the agent.")
    parser.add_argument("--date", help="Date of the memory to process (YYYY-MM-DD). Defaults to yesterday.", default=(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    parser.add_argument("--api-base", default=os.environ.get("LLM_API_BASE", "https://api.openai.com/v1"), help="OpenAI-compatible API Base URL")
    parser.add_argument("--api-key", default=os.environ.get("LLM_API_KEY", ""), help="API Key")
    parser.add_argument("--model", default=os.environ.get("LLM_MODEL", "gpt-4o"), help="Model to use")
    parser.add_argument("--temperature", type=float, default=float(os.environ.get("MEDITATION_TEMPERATURE", "0.3")), help="Temperature for generation")
    parser.add_argument("--api-type", default=os.environ.get("LLM_API_TYPE", ""), help="API Type (openai or anthropic)")
    parser.add_argument("--retries", type=int, default=int(os.environ.get("LLM_RETRIES", "2")), help="Retry count for transient LLM failures")
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
    response = call_llm(args.api_base, args.api_key, args.model, prompt, args.api_type, args.temperature, args.retries)
    if not response:
        return

    new_memory_match = re.search(r"<new_memory>\s*(.*?)\s*</new_memory>", response, re.DOTALL | re.IGNORECASE)
    evo_match = re.search(r"<evolution>\s*(.*?)\s*</evolution>", response, re.DOTALL | re.IGNORECASE)

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
