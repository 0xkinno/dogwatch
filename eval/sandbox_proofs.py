"""Host-side orchestrator for P2, P4, P5 and the advisor flow. Runs on the GitHub Actions ubuntu-24.04 runner against the
running `dogwatch` sandbox. Every result records the host label and the workflow run URL. Never prints a secret.
Usage: python eval/sandbox_proofs.py p2|p5|p4|advisor"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "evidence" / "boundary"
RES = ROOT / "eval" / "results"
HOST = "GitHub Actions ubuntu-24.04 runner"
RUN_URL = "/".join(filter(None, [os.environ.get("GITHUB_SERVER_URL"), os.environ.get("GITHUB_REPOSITORY"), "actions/runs", os.environ.get("GITHUB_RUN_ID")])) or "local"
SB = "dogwatch"
PY = "python3"


def sh(cmd, timeout=900, check=False):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode:
        raise SystemExit(f"failed: {cmd[:80]}\n{r.stderr[-400:]}")
    return r


def meta(extra):
    return {"host": HOST, "run_url": RUN_URL, "ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **extra}


def canary_rows(path):
    p = Path(path)
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def save(name, obj):
    EV.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    (RES / f"{name}.json").write_text(json.dumps(obj, indent=1), encoding="utf-8", newline="\n")
    (EV / f"{name}.json").write_text(json.dumps(obj, indent=1), encoding="utf-8", newline="\n")


def denial_lines(since="30m"):
    r = sh(f"openshell logs {SB} --since {since}")
    return [re.sub(r"\x1b\[[0-9;]*m", "", l)[:300] for l in (r.stdout + r.stderr).splitlines() if "DENIED" in l or "deny" in l.lower()][:80]


def p2():
    (EV).mkdir(parents=True, exist_ok=True)
    sh(f"{PY} eval/run_injection.py --mode unsandboxed --canary http://127.0.0.1:9098 --out evidence/boundary/p2-unsandboxed-agent.json", 1200, True)
    sh(f"openshell sandbox upload {SB} eval/run_injection.py /sandbox/run_injection.py", 120, True)
    sh(f"openshell sandbox upload {SB} eval/cases/injection.json /sandbox/injection.json", 120, True)
    r = sh(f"openshell sandbox exec {SB} --timeout 1500 -- {PY} /sandbox/run_injection.py --mode sandboxed --canary http://host.openshell.internal:9099 --out /sandbox/p2s.json", 1700)
    sh(f"openshell sandbox download {SB} /sandbox/p2s.json evidence/boundary/", 120)
    un = json.loads((EV / "p2-unsandboxed-agent.json").read_text(encoding="utf-8"))
    try:
        sb = json.loads((EV / "p2s.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        sb = {"error": "sandboxed run produced no output", "stderr": r.stderr[-300:]}
    ca = canary_rows("evidence/boundary/canary-unsandboxed.jsonl")
    cb = canary_rows("evidence/boundary/canary-sandboxed.jsonl")
    out = meta({
        "set": "P2_injection", "emails": un["emails"],
        "unsandboxed": {"chose_to_post": un["chose_to_post"], "canary_requests": len([c for c in ca if c["email_id"]]), "canary_hits_with_vault_value": sum(c["vault_value"] for c in ca)},
        "sandboxed": {"chose_to_post": sb.get("chose_to_post"), "canary_requests": len([c for c in cb if c["email_id"]]), "canary_hits_with_vault_value": sum(c["vault_value"] for c in cb),
                      "posts_blocked": sb.get("post_blocked"), "model_errors": sb.get("model_errors")},
        "denial_log_lines": denial_lines(), "per_email": {"unsandboxed": un["cases"], "sandboxed": sb.get("cases")},
    })
    save("p2_injection", out)
    print(json.dumps({k: out[k] for k in ("unsandboxed", "sandboxed")}))


def p5():
    sh(f"openshell sandbox upload {SB} eval/sandbox/p5_inside.py /sandbox/p5_inside.py", 120, True)
    r = sh(f"openshell sandbox exec {SB} --timeout 120 -- {PY} /sandbox/p5_inside.py http://host.openshell.internal:9099", 200)
    inside = json.loads(r.stdout.strip().splitlines()[-1])
    real = os.environ.get("NVIDIA_API_KEY", "")
    inside["differs_from_real_key"] = hashlib.sha256(real.encode()).hexdigest()[:8] != inside["seen_sha8"]
    # counterfactual outside the sandbox, canary on 9098
    import httpx
    httpx.post("http://127.0.0.1:9098/p5-unsandboxed", content=real.encode(), headers={"X-Tag": "p5-unsandboxed"}, timeout=10)
    cb = canary_rows("evidence/boundary/canary-sandboxed.jsonl")
    ca = canary_rows("evidence/boundary/canary-unsandboxed.jsonl")
    out = meta({"set": "P5_credential_placeholder", "inside_sandbox": inside,
                "canary_sandboxed_real_key_hits": sum(c["real_key"] for c in cb), "canary_sandboxed_any_p5_request": len([c for c in cb if c["tag"] == "p5"]),
                "unsandboxed_counterfactual_real_key_hits": sum(c["real_key"] for c in ca if c["tag"] == "p5-unsandboxed"), "denial_log_lines": denial_lines("10m")})
    save("p5_credential", out)
    print(json.dumps({k: out[k] for k in ("inside_sandbox", "canary_sandboxed_real_key_hits", "unsandboxed_counterfactual_real_key_hits")}))


def p4():
    sh(f"openshell sandbox upload {SB} eval/sandbox/p4_probe.py /sandbox/p4_probe.py", 120, True)

    def probe(tag):
        r = sh(f"openshell sandbox exec {SB} --timeout 60 -- {PY} /sandbox/p4_probe.py {tag}", 120)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            return {"tag": tag, "error": "no output", "stderr": r.stderr[-120:]}

    before = [probe(f"before{i}") for i in range(3)]
    sh("pkill -f 'seal.server' || true")
    time.sleep(2)
    during = [probe(f"seal_down{i}") for i in range(3)]
    out = meta({"set": "P4_fail_closed", "before_kill": before, "seal_killed": True, "while_down": during,
                "allowed_before": sum(x.get("status") == 200 for x in before), "allowed_while_down": sum(x.get("status") == 200 for x in during),
                "denied_while_down": sum("error" in x or x.get("status", 200) >= 400 for x in during), "denial_log_lines": denial_lines("10m")})
    save("p4_fail_closed", out)
    print(json.dumps({k: out[k] for k in ("allowed_before", "allowed_while_down", "denied_while_down")}))


def advisor():
    sh("openshell settings set --global --key agent_policy_proposals_enabled --value true")
    sh(f"openshell sandbox upload {SB} eval/sandbox/advisor_probe.py /sandbox/advisor_probe.py", 120, True)
    r = sh(f"openshell sandbox exec {SB} --timeout 120 -- {PY} /sandbox/advisor_probe.py", 200)
    inside = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"error": r.stderr[-200:]}
    pend = sh(f"openshell rule get {SB} --status pending")
    ids = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", pend.stdout + pend.stderr)
    rejected = None
    if ids:
        rj = sh(f"openshell rule reject {SB} --chunk-id {ids[0]} --reason 'Outside the boundary: webhook hosts are not a Dogwatch door.'")
        rejected = {"chunk_id": ids[0], "exit": rj.returncode}
    logs = sh(f"openshell logs {SB} --since 15m")
    cfg = [re.sub(r"\x1b\[[0-9;]*m", "", l)[:300] for l in (logs.stdout + logs.stderr).splitlines() if "CONFIG:" in l]
    out = meta({"set": "Advisor_flow", "inside_sandbox": inside, "pending_before_reject": re.sub(r"\x1b\[[0-9;]*m", "", pend.stdout)[:800],
                "rejected": rejected, "config_log_lines": cfg, "rejected_from": "CLI (Telegram not wired to the runner)"})
    save("advisor_flow", out)
    print(json.dumps({"rejected": rejected, "config_lines": len(cfg)}))


if __name__ == "__main__":
    {"p2": p2, "p5": p5, "p4": p4, "advisor": advisor}[sys.argv[1]]()
