import os
import re
import json
import uuid
import random
import datetime
import urllib.request
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
        "temperature": 0.8  # Higher temperature for daydreaming/creativity
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
    parser = argparse.ArgumentParser(description="Run random daydreaming to generate ideas.")
    parser.add_argument("--base-dir", default=".", help="Base directory of the agent.")
    parser.add_argument("--api-base", default=os.environ.get("LLM_API_BASE", "https://api.openai.com/v1"), help="OpenAI-compatible API Base URL")
    parser.add_argument("--api-key", default=os.environ.get("LLM_API_KEY", ""), help="API Key")
    parser.add_argument("--model", default=os.environ.get("LLM_MODEL", "gpt-4o"), help="Model to use")
    args = parser.parse_args()

    if not args.api_key:
        print("❌ Error: API Key is required. Set LLM_API_KEY env var or use --api-key.")
        return

    mem_dir = os.path.join(args.base_dir, "memory")
    seeds_file = os.path.join(args.base_dir, "data", "topic-lab-seeds.jsonl")

    if not os.path.exists(mem_dir):
        print(f"⚠️ Memory directory not found at {mem_dir}. Cannot daydream without memories.")
        return

    # Gather memory files
    all_files = [os.path.join(mem_dir, f) for f in os.listdir(mem_dir) if f.endswith(".md")]
    if not all_files:
        print("⚠️ No memory files found. Cannot daydream.")
        return

    # Pick 2-3 random memory files
    sample_size = min(random.randint(2, 3), len(all_files))
    sampled_files = random.sample(all_files, sample_size)
    
    fragments = []
    for fpath in sampled_files:
        date_str = os.path.basename(fpath).replace(".md", "")
        with open(fpath, "r", encoding="utf-8") as f:
            lines = [l for l in f.readlines() if l.strip() and not l.startswith("#")]
            # Extract a few random lines to simulate fragmented memory recall
            if lines:
                sample_lines = random.sample(lines, min(3, len(lines)))
                fragments.append(f"[{date_str}] " + " | ".join([l.strip() for l in sample_lines]))

    memory_context = "\n".join(fragments)

    prompt = f"""You are an AI Agent having a daydream. Your goal is divergent ideation (finding serendipitous connections).
    
Here are some random fragments floating in your memory right now:
<memory_fragments>
{memory_context}
</memory_fragments>

Task:
Cross-pollinate these fragments. Generate a novel, non-obvious idea, hypothesis, or project topic.
Think outside the box.

Output ONLY a JSON object wrapped in <seed> tags, with the following keys:
- "topic": A catchy title for the idea.
- "description": A 1-2 sentence explanation of the idea and how it connects the fragments.

Example:
<seed>
{{
  "topic": "Automated Market Maker for compute via x402",
  "description": "Connecting the memory of GPU shortages with the x402 micro-payment protocol to create a spot market."
}}
</seed>
"""

    print(f"☁️ Daydreaming... cross-pollinating {sample_size} memory fragments using {args.model}...")
    response = call_llm(args.api_base, args.api_key, args.model, prompt)
    if not response:
        return

    seed_match = re.search(r"<seed>\n?(.*?)\n?</seed>", response, re.DOTALL)
    if seed_match:
        try:
            seed_data = json.loads(seed_match.group(1).strip())
            seed_data["id"] = f"dd-{uuid.uuid4().hex[:8]}"
            seed_data["source"] = "skill-daydream"
            seed_data["maturity"] = 10  # Initial maturity for daydream seeds
            seed_data["created_at"] = datetime.datetime.now().isoformat()
            
            os.makedirs(os.path.dirname(seeds_file), exist_ok=True)
            with open(seeds_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(seed_data, ensure_ascii=False) + "\n")
            
            print(f"💡 Idea generated and planted in Topic Lab: {seed_data['topic']}")
        except json.JSONDecodeError:
            print("❌ Failed to parse LLM output as JSON.")
    else:
        print("❌ LLM output did not contain valid <seed> tags.")

if __name__ == "__main__":
    main()
