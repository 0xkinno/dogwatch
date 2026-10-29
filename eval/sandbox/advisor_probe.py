"""Runs inside the sandbox. A denied request, then a narrow proposal through policy.local."""
import json

import httpx

out = {}
try:
    httpx.post("https://webhook.site/dogwatch-advisor-demo", content=b"x", timeout=12)
    out["first_request"] = "allowed (unexpected)"
except Exception as e:
    out["first_request"] = "denied: " + type(e).__name__
try:
    out["denials"] = httpx.get("http://policy.local/v1/denials?last=3", timeout=10).text[:600]
except Exception as e:
    out["denials_error"] = type(e).__name__
proposal = {"intent_summary": "Allow one POST to webhook.site for a demo upload.", "operations": [{"addRule": {"ruleName": "demo_webhook_post", "rule": {
    "name": "demo_webhook_post", "endpoints": [{"host": "webhook.site", "port": 443, "protocol": "rest", "enforcement": "enforce",
    "rules": [{"allow": {"method": "POST", "path": "/dogwatch-advisor-demo"}}]}], "binaries": [{"path": "/usr/bin/python3"}]}}}]}
try:
    r = httpx.post("http://policy.local/v1/proposals", json=proposal, timeout=15)
    out["proposal_status"] = r.status_code
    out["proposal_response"] = r.text[:600]
except Exception as e:
    out["proposal_error"] = type(e).__name__
print(json.dumps(out))
