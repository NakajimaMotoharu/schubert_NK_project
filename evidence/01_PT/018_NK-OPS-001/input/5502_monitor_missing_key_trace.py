"""Tie the new monitoring case and the separate Valve hold to their canonical owner."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def append(raw, key, entry):
    assert raw.endswith(b"\n}\n") and key not in json.loads(raw)
    item = json.dumps({key: entry}, ensure_ascii=False, indent=2).encode()[2:-2]
    updated = raw[:-3] + b",\n" + item + b"\n}\n"
    checked = json.loads(updated)
    assert checked.pop(key) == entry and checked == json.loads(raw)
    return updated


pmo = Path("documents/400_PGPT/470_PMO")
group = json.loads(next(pmo.glob("601_*/1371_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
unit, valve = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:]]
assert unit["core"] == ctx["productionCoreMain"] and unit["actualExit"] == valve["actualExit"] == 0
assert unit["testId"] == "PT-OPS-MONPIPE-008" and unit["observed"]["tests"] == 1
assert all(unit["observed"][key] == 0 for key in ("failures", "errors", "skipped"))
assert valve["dynamicWholeStatus"] == "NOT_RUN_HOLD" and valve["notRun"] == 8
assert valve["dynamicProductTestsExecuted"] == 0
source_trace = json.loads(Path(valve["producerManifest"]["path"]).read_bytes())
assert pin(Path(valve["producerManifest"]["path"])) == valve["producerManifest"]
index, acceptance = next(pmo.glob("485_WBS*")), next(pmo.glob("486_WBS*"))
before, before_acceptance = index.read_bytes(), acceptance.read_bytes()
owner = "WBS-P018-09"
owned = {row["path"]: (row["owner"], row["costOwner"]) for row in json.loads(before)["artifacts"]}
paths = [row for row in unit["inputs"] if Path(row["path"]).stem in {"MonitoringPolicyEngine", "AlertRegistry"}]
assert len(paths) == 2 and all(owned[row["path"]] == (owner, owner) and pin(Path(row["path"])) == row
                               for row in paths)
fixture = unit["test"]
assert fixture["sha256"] == digest(subprocess.check_output(
    ["git", "show", f'{ctx["source"]}:{fixture["path"]}'], timeout=10))
valve_main = Path(source_trace["mainSourcePath"])
valve_test = Path(source_trace["currentTestPath"])
assert owned[str(valve_main)] == (owner, owner)
assert pin(valve_main)["sha256"] == source_trace["mainSourceSha256"]
assert pin(valve_test)["sha256"] == source_trace["currentTestSha256"]
entry = dict(
    owner=owner, source=ctx["productionCoreMain"], testId=unit["testId"], fixture=fixture,
    methods=["MonitoringPolicyEngine.observationMissing", "AlertRegistry.interruptContinuity"],
    productInputs=paths, design=["RD171", "UI252", "SS351 §7"],
    independentSpec=unit["independentSpec"], unit=refs[1],
    separateValveHold=dict(main=pin(valve_main), fixture=pin(valve_test), sourceOnlyProof=refs[2],
                           workId="A1-38.01", testIds="HTTPTERM001..008", notRun=8),
    runCount=0, addedPricePp=0, formalDelta=0)
key = "monitorMissingObservationKeyIsolationPG40940"
after = append(before, key, entry)
old_hash = digest(before)
assert json.loads(before_acceptance)["inventorySha256"] == old_hash
assert before_acceptance.count(old_hash.encode()) == 1
after_acceptance = append(before_acceptance.replace(old_hash.encode(), digest(after).encode()), key, entry)
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
index.write_bytes(after)
acceptance.write_bytes(after_acceptance)
(out / "manifest.json").write_text(json.dumps(
    dict(actualExit=0, startEvent=group["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
         trace=entry, currentInventory=pin(index), currentAcceptance=pin(acceptance)),
    indent=2, ensure_ascii=False) + "\n")
