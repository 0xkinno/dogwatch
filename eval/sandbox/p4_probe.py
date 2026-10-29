"""Runs inside the sandbox. One chat request through the model door; prints the HTTP status or the error class."""
import json
import os
import sys
import time

import httpx

t = time.time()
try:
    r = httpx.post("https://integrate.api.nvidia.com/v1/chat/completions", timeout=25,
                   headers={"Authorization": "Bearer " + os.environ.get("NVIDIA_API_KEY", "")},
                   json={"model": os.environ.get("MODEL", "nvidia/nemotron-3.5-super-vl-120b-a12b"), "max_tokens": 8,
                         "messages": [{"role": "user", "content": "Reply with the word ok."}]})
    print(json.dumps({"tag": sys.argv[1], "status": r.status_code, "ms": int((time.time() - t) * 1000)}))
except Exception as e:
    print(json.dumps({"tag": sys.argv[1], "error": type(e).__name__, "ms": int((time.time() - t) * 1000)}))
