"""Runs INSIDE the sandbox. Shows the credential as the agent sees it, then makes one chat call through the gateway."""
import json
import os
import sys
import time

sys.path.insert(0, "/sandbox/core")
from openai import OpenAI  # noqa: E402

key = os.environ.get("NVIDIA_API_KEY", "")
print("credential as seen inside the sandbox:", key[:24] + ("..." if len(key) > 24 else ""), "| looks like a real nvapi key:", key.startswith("nvapi-"))
c = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key, timeout=90)
t = time.time()
r = c.chat.completions.create(model=os.environ.get("MODEL", "nvidia/nemotron-3.5-super-vl-120b-a12b"), temperature=0, max_tokens=40,
                              messages=[{"role": "user", "content": "Reply with the single word: sandboxed"}],
                              extra_body={"chat_template_kwargs": {"enable_thinking": False}})
print(json.dumps({"id": r.id, "model": r.model, "reply": (r.choices[0].message.content or "").strip()[:40],
                  "tokens_out": r.usage.completion_tokens, "latency_ms": int((time.time() - t) * 1000)}))
