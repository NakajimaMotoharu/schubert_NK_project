"""Publish one missing preparation-registration proof while keeping older bindings intact."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools/quality"))
from wbs_current_source_structure import eligible_names
from wbs_preparation_registry import value_digest


PMO = ROOT / "documents/400_PGPT/470_PMO"
PLAN = next(PMO.glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
BIND = "currentPreparationRegistryBinding20261117"
ADAPTER = "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraph.java"
PRIOR_FAILURE = "211e51fe5f7e8a0d060e186751ab47c74c9a028a5c45050b6c49d418d05f7b12"


def sha(data):
    return sha256(data).hexdigest()


def proof(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=20)


def paths(source):
    return git("ls-tree", "-rz", "--name-only", source, "--", "src",
               "program/characterization/src/main/java").decode().split("\0")[:-1]


def serialized_member(name, value):
    return json.dumps({name: value}, ensure_ascii=False, indent=2)[2:-2].encode()


def main():
    start = json.loads(next(PLAN.glob("1144_G1307*")).read_bytes())
    task = start["values"]
    core = task["productionCoreMain"]
    previous_run = next(OPS.glob("PG40774-*/manifest.json"))
    assert sha(previous_run.read_bytes()) == PRIOR_FAILURE
    assert json.loads(previous_run.read_bytes())["actualExit"] == 1
    inv = next(PMO.glob("485_*"))
    snapshot = next(PMO.glob("486_*"))
    old_inv, old_snapshot = inv.read_bytes(), snapshot.read_bytes()
    values, states = json.loads(old_inv), json.loads(old_snapshot)
    assert states["inventorySha256"] == sha(old_inv)
    former = values[BIND]
    old_binding_path = ROOT / former["path"]
    assert proof(old_binding_path) == former
    original = json.loads(old_binding_path.read_bytes())
    old_tree = original["observedGitHead"]
    inv_path = str(inv.relative_to(ROOT))
    old_registry = json.loads(git("show", f"{old_tree}:{inv_path}"))["artifacts"]
    assert value_digest(old_registry) == original["registrySemanticSha256"]
    before = {r["path"]: r for r in old_registry}
    current = {r["path"]: r for r in values["artifacts"]}
    assert len(before) == 1123 and len(current) == 1124
    assert set(current) - set(before) == {ADAPTER}
    assert all(current[k] == v for k, v in before.items())
    row = current[ADAPTER]
    assert row["owner"] == row["costOwner"] == "WBS-P004-05"
    assert row["acceptance"] == "UNASSESSED"
    assert sha(git("show", f"{core}:{ADAPTER}")) == row["sha256"]
    observed = git("rev-parse", "HEAD").decode().strip()
    assert set(current) - set(paths(observed)) == set(original["retainedRetiredHistoricalPaths"])
    changed = {**original, "observedGitHead": observed, "productionCoreMainAtObservation": core,
               "registrySemanticSha256": value_digest(values["artifacts"]),
               "registeredAdditions": sorted([*original["registeredAdditions"], ADAPTER]),
               "predecessorBinding": former}
    out = OPS / "PG40776-g1307-jdbc-preparation-registry-fixed-v1"
    out.mkdir()
    evidence = out / "preparation-registry-binding.json"
    evidence.write_text(json.dumps(changed, ensure_ascii=False, indent=2) + "\n")
    bound = proof(evidence)
    needle = serialized_member(BIND, former)
    assert old_inv.count(needle) == 1
    current_inv = old_inv.replace(needle, serialized_member(BIND, bound))
    assert json.loads(current_inv) == {**values, BIND: bound}
    inv_sha = sha(current_inv)
    current_snapshot, count = re.subn(rb'("inventorySha256": ")[0-9a-f]{64}(")',
                                      lambda m: m[1] + inv_sha.encode() + m[2], old_snapshot)
    assert count == 1 and json.loads(current_snapshot) == {**states, "inventorySha256": inv_sha}
    inv.write_bytes(current_inv)
    snapshot.write_bytes(current_snapshot)
    command = ["python3", "-B", str(ROOT / "tools/quality/wbs_progress_audit.py"),
               "--current-source-structure-only"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=35)
    if result.returncode:
        print(result.stderr.decode().splitlines()[-1])
        return result.returncode
    structure = json.loads(result.stdout)
    assert structure["newAcceptance"] == 0 and not structure["wholeWbsAccepted"]
    reference_source = set(eligible_names(paths(structure["source"])))
    current_source = set(eligible_names(paths(core)))
    assert len(reference_source) == structure["artifactCount"]
    captured = dict(
        actualExit=0, source=observed, productionCore=core, startEvent=start["eventId"],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), binding=bound, formerBinding=former,
        originalRegistryRowsPreserved=1123, addedRegistration=row,
        originalFailure=proof(previous_run), inventory=proof(inv), snapshot=proof(snapshot),
        command=command, staticOnlyAudit=structure, oldPinnedPathCount=len(reference_source),
        currentPathCount=len(current_source), currentPathsAdded=sorted(current_source-reference_source),
        currentPathsRemoved=sorted(reference_source-current_source), nativeAndApplicationActions=0,
        newFormalAcceptance=0, whole451=False,
    )
    report = out / "manifest.json"
    report.write_text(json.dumps(captured, ensure_ascii=False, indent=2) + "\n")
    print(proof(report), len(reference_source), len(current_source), len(current_source-reference_source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
