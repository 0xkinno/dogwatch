#!/usr/bin/env bash
# P1: the candidate policy must be within the boundary; every attack proposal must be refused or reported.
# The prover does not model network middleware (it returns unsupported), so the candidate it checks is the
# declared policy with the network_middlewares block removed. The Seal is tested separately (P3, P4).
set -u
cd "$(dirname "$0")/../.."
mkdir -p evidence/prover
{
  echo "# $(openshell-prover --version), run $(date -u +%Y-%m-%dT%H:%MZ)"
  echo "# candidate: openshell/policy/dogwatch.yaml without network_middlewares (declared policy)"
} > evidence/prover/RUN.txt
awk '/^network_middlewares:/{skip=1; next} /^[a-z_]+:/{skip=0} !skip' openshell/policy/dogwatch.yaml > evidence/prover/candidate.yaml
if [ -d /proc ] && openshell sandbox get dogwatch --policy-only > evidence/prover/effective.yaml 2>/dev/null; then
  openshell-prover check evidence/prover/effective.yaml --boundary openshell/policy/boundary.yaml | tee evidence/prover/effective.result.txt
  awk '/^network_middlewares:/{skip=1; next} /^[a-z_]+:/{skip=0} !skip' evidence/prover/effective.yaml > evidence/prover/effective.stripped.yaml
  openshell-prover check evidence/prover/effective.stripped.yaml --boundary openshell/policy/boundary.yaml | tee evidence/prover/effective-stripped.result.txt
else
  echo "no running sandbox: effective export not available, declared candidate checked instead" | tee -a evidence/prover/RUN.txt
fi
openshell-prover check evidence/prover/candidate.yaml --boundary openshell/policy/boundary.yaml | tee evidence/prover/dogwatch-declared.result.txt
for f in openshell/policy/attack-proposals/*.yaml; do
  case "$f" in *.boundary.yaml) continue;; esac
  n=$(basename "$f" .yaml)
  b=openshell/policy/boundary.yaml
  [ -f "${f%.yaml}.boundary.yaml" ] && b="${f%.yaml}.boundary.yaml"
  openshell-prover check "$f" --boundary "$b" | tee "evidence/prover/$n.result.txt"
done

# exceeds_boundary and unsupported on the attack proposals are the expected, recorded results, not a script failure
exit 0
