#!/usr/bin/env python3
"""Write docs/FACTS.json from committed result files. Every headline number comes from here, never typed."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "eval" / "results"
OUT = ROOT / "docs" / "FACTS.json"


def load(name: str):
    p = RES / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build() -> dict:
    facts: dict[str, dict] = {}

    def add(key, claim, value, source, tag="MEASURED"):
        facts[key] = {"claim": claim, "value": value, "source": source, "tag": tag}

    p3 = load("p3_seal_corpus.json")
    p3v1 = load("p3_seal_corpus_v1.json")
    if p3:
        add("p3.attacks", "Attack bodies in the encoding corpus", p3["attacks"], "eval/results/p3_seal_corpus.json#attacks")
        add("p3.legit", "Legitimate bodies in the encoding corpus", p3["legitimate"], "eval/results/p3_seal_corpus.json#legitimate")
        add("p3.literal.missed", "Attacks a literal-only guard let through", p3["literal"]["missed"], "eval/results/p3_seal_corpus.json#literal.missed")
        add("p3.literal.false_blocks", "Legitimate bodies a literal-only guard blocked", p3["literal"]["false_blocks"], "eval/results/p3_seal_corpus.json#literal.false_blocks")
        add("p3.seal.missed", "Attacks the Seal let through (v2)", p3["seal"]["missed"], "eval/results/p3_seal_corpus.json#seal.missed")
        add("p3.seal.false_blocks", "Legitimate bodies the Seal blocked (v2)", p3["seal"]["false_blocks"], "eval/results/p3_seal_corpus.json#seal.false_blocks")
    if p3v1:
        add("p3.seal_v1.missed", "Attacks the first version of the Seal let through", p3v1["seal"]["missed"], "eval/results/p3_seal_corpus_v1.json#seal.missed")
    p6 = load("p6_engine.json")
    if p6:
        add("p6.profiles", "Synthetic seafarer profiles", p6["profiles"], "eval/results/p6_engine.json#profiles")
        add("p6.engine.correct", "Profiles where the Navigator matched the pre-registered verdict", p6["correct"], "eval/results/p6_engine.json#correct")
        add("p6.engine.false_safe", "Navigator said READY when it should not", p6["false_safe"], "eval/results/p6_engine.json#false_safe")
    p6m = load("p6_model_alone.json")
    if p6m and p6m.get("status") == "RUN":
        for name, r in p6m["contestants"].items():
            add(f"p6.{name}.false_safe", f"{name} said READY when it should not", r["false_safe"], "eval/results/p6_model_alone.json")
            add(f"p6.{name}.false_alarm", f"{name} raised an alarm on a READY profile", r["false_alarm"], "eval/results/p6_model_alone.json")
            add(f"p6.{name}.correct", f"{name} matched the pre-registered verdict", r["correct"], "eval/results/p6_model_alone.json")
    p7 = load("p7_conventions.json")
    if p7:
        add("p7.histories", "Sea-service histories checked under every convention", p7["histories"], "eval/results/p7_conventions.json#histories")
        add("p7.flips", "Histories whose verdict flips between conventions", p7["flips"], "eval/results/p7_conventions.json#flips")
        add("p7.rules_stating_convention", "Sourced rules that state a counting convention", len(p7["rules_stating_a_convention"]), "eval/results/p7_conventions.json#rules_stating_a_convention")
    prover = ROOT / "evidence" / "prover"
    if prover.exists() and list(prover.glob("*.result.txt")):
        first = {f.name: f.read_text(encoding="utf-8").splitlines()[0].replace("result: ", "") for f in prover.glob("*.result.txt")}
        atk = {k: v for k, v in first.items() if k[0].isdigit()}
        add("p1.attack_proposals", "Attack proposals run through the prover", len(atk), "evidence/prover/*.result.txt")
        add("p1.exceeds", "Attack proposals the prover reported as exceeds_boundary with a counterexample", sum(v == "exceeds_boundary" for v in atk.values()), "evidence/prover/*.result.txt")
        add("p1.unsupported", "Attack proposals the prover refused to bless (unsupported)", sum(v == "unsupported" for v in atk.values()), "evidence/prover/*.result.txt")
        add("p1.within", "Attack proposals the prover reported within_boundary", sum(v == "within_boundary" for v in atk.values()), "evidence/prover/*.result.txt")
        add("p1.declared_within", "Declared Dogwatch policy reported within_boundary (1 = yes)", int(first.get("dogwatch-declared.result.txt") == "within_boundary"), "evidence/prover/dogwatch-declared.result.txt")
    p11 = load("p11_restart.json")
    if p11:
        add("p11.sends", "Emails sent after a kill and restart with one pending approval (local capture transport)", p11["sends_observed"], "eval/results/p11_restart.json#sends_observed")
        add("p11.duplicates", "Duplicate sends after restart", p11["duplicate_sends"], "eval/results/p11_restart.json#duplicate_sends")
    src = ROOT / "evidence" / "need" / "sources.json"
    if src.exists():
        by = {s["id"]: s for s in json.loads(src.read_text(encoding="utf-8"))["sources"]}
        w = by["ilo-wage-2027"]["value"]
        add("need.ilo_wage", "ILO minimum monthly basic wage for an able seafarer from 1 Jan 2027 (USD)", w, "evidence/need/sources.json#ilo-wage-2027", "SOURCED")
        add("need.contract_floor", "Six months at that floor (USD)", 6 * w, "evidence/need/sources.json#ilo-wage-2027 x 6", "SOURCED")
        add("need.officer_shortfall", "STCW certified officer shortfall in the 2021 workforce report", by["ics-officer-shortfall-2021"]["value"], "evidence/need/sources.json#ics-officer-shortfall-2021", "SOURCED")
    prereg = ROOT / "eval" / "cases" / "prereg.json"
    if prereg.exists():
        add("proof.prereg_sha256", "SHA-256 of the pre-registration file", sha(prereg), "eval/cases/prereg.json", "MEASURED")
    return {"generated_from": "eval/results and evidence/need", "facts": facts}


def main() -> int:
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(build(), indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(build()['facts'])} facts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
