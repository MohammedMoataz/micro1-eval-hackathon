"""One thin client for any OpenAI-compatible endpoint (default: OpenRouter). Stdlib only."""
import json
import os
import urllib.request

URL = os.environ.get("EVAL_API_URL", "https://openrouter.ai/api/v1/chat/completions")


def complete(model: str, prompt: str, temperature: float = 0.0) -> str:
    key = os.environ["OPENROUTER_API_KEY"]
    body = json.dumps({
        "model": model,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        URL, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"]
