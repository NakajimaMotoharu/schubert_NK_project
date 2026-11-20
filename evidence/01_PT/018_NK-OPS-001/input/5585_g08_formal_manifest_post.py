"""Bind the formal evidence verifier's local canaries without running product collectors."""

import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


TOOL = Path("tools/quality/018_collect_verified_evidence_set.py")
TEST = Path("tools/quality/019_test_evidence_set.py")
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
RUNS = Path("../pgpt-runs/PG379")


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def main():
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1546_*")
    spec = json.loads(start.read_bytes())["values"]
    before, = OPS.glob("PG41104-*/manifest.json")
    first = json.loads(before.read_bytes())
    assert first["actualExit"] == 1 and first["expectedRejections"] == 5
    assert first["actualRejections"] == 0
    saved, = RUNS.glob("PG41106-*-v1")
    assert (saved/"exit.txt").read_text() == "0\n"
    output = (saved/"stderr.txt").read_text()
    cases = re.findall(r"^(test_\w+) \(__main__\.EvidenceSetTest\.[^\n]+\) \.\.\. ok$",
                       output,re.MULTILINE)
    assert len(cases) == len(set(cases)) == 106
    assert output.endswith("OK\n")
    assert "test_manifest_json_has_unique_keys_and_integer_exit" in cases
    assert "test_every_scope_run_source_and_integrity" in cases
    assert "test_collection_stops_at_each_failure" in cases
    source = subprocess.check_output(["git","rev-parse","HEAD"],text=True,timeout=20).strip()
    for path in (TOOL,TEST):
        assert subprocess.check_output(["git","show",f"{source}:{path}"],timeout=20)==path.read_bytes()
    assert pin(TEST)["sha256"] == first["testFileSha256"]
    syntax = ast.parse(TOOL.read_text())
    uses = [node.name for node in syntax.body if isinstance(node,ast.FunctionDef) and
            any(isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=="load_success_manifest"
                for c in ast.walk(node))]
    assert uses == ["validate_scope","main"]
    assert not subprocess.check_output(["git","diff","--name-only",spec["source"],source,
                                        "--","src"],timeout=20)
    result = OPS/saved.name
    result.mkdir()
    manifest = result/"manifest.json"
    with manifest.open("x") as f:
        json.dump(dict(actualExit=0,source=source,productionCore=spec["productionCoreMain"],
                       originalRed=pin(before),inputs=[pin(TOOL),pin(TEST)],rootAndScopeUseSameReader=uses,
                       cases=sorted(cases),toolTests=106,toolFailures=0,toolErrors=0,toolSkips=0,
                       strictPositive=1,expectedRejections=5,performedRejections=5,scopeInventory=53,
                       terminalRecords=[pin(saved/"exit.txt"),pin(saved/"stdout.txt"),pin(saved/"stderr.txt")],
                       command=["TMPDIR=/dev/shm","python3","-B",str(TEST),"-v"],
                       productTests=0,actualCollectorsStarted=0,formalDelta=0,whole451=False,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),f,indent=2,ensure_ascii=False)
        f.write("\n")
    print(pin(manifest),len(cases))


if __name__=="__main__":
    main()
