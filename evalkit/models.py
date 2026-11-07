"""One thin client for OpenAI-compatible endpoints. Stdlib only.

Model ids starting with "gemini-" go to Google AI Studio (free tier, GEMINI_API_KEY);
everything else goes to OpenRouter (OPENROUTER_API_KEY), e.g. "google/gemma-4-31b-it:free".
"""
import json
import os
import time
import urllib.error
import urllib.request

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GOOGLE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


def endpoint(model: str):
    # Read env at call time, so values loaded from .env after import still apply.
    if model.startswith("gemini-"):
        return GOOGLE_URL, os.environ["GEMINI_API_KEY"]
    return os.environ.get("EVAL_API_URL", OPENROUTER_URL), os.environ["OPENROUTER_API_KEY"]


def complete(model: str, prompt: str, temperature: float = 0.0) -> str:
    url, key = endpoint(model)
    body = json.dumps({
        "model": model,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        url, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    )
    for wait in (15, 45, 0):  # free tiers rate-limit often: retry 429 twice, then give up
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code != 429 or not wait:
                raise
            time.sleep(wait)
