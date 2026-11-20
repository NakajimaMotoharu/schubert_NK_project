"""Trace RRF-PURE-009 to its assigned DAO and its exact unit and style receipts."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def append(raw, key, entry):
    retained = json.loads(raw)
    assert key not in retained and raw.endswith(b"\n}\n")
    member = json.dumps({key: entry}, ensure_ascii=False, indent=2).encode()[2:-2]
    updated = raw[:-3] + b",\n" + member + b"\n}\n"
    restored = json.loads(updated)
    assert restored.pop(key) == entry and restored == retained
    return updated


pmo = Path("documents/400_PGPT/470_PMO")
group = json.loads(next(pmo.glob("601_*/1337_*")).read_bytes())
ctx = group["values"]
previous, unit_ref, style_ref, lineage_ref = ctx["oracleReferences"]
assert all(pin(Path(receipt["path"])) == receipt
           for receipt in (previous, unit_ref, style_ref, lineage_ref))
unit, style, lineage = [json.loads(Path(ref["path"]).read_bytes())
                        for ref in (unit_ref, style_ref, lineage_ref)]
core = ctx["productionCoreMain"]
test_id = "RRF-PURE-009"
assert unit["source"] == style["source"] == core
assert unit["testId"] == style["testId"] == test_id and unit["actualExit"] == style["actualExit"] == 0
assert unit["fixture"] == style["fixture"]
assert pin(Path(unit["fixture"]["path"])) == unit["fixture"]
assert pin(Path(unit["independentOracle"]["path"])) == unit["independentOracle"]
assert lineage["originalRun"]["tests"] == 8
assert unit["observedJUnit"] == dict(tests=1, failures=0, errors=0, skipped=0)
assert style["observedFiles"] == 1 and style["observedFindings"] == 0
dao, = (row for row in unit["sourceClosure"] if row["path"].endswith("/RunReferenceRepository.java"))
assert digest(subprocess.check_output(["git", "show", f"{core}:{dao['path']}"], timeout=10)) == dao["sha256"]
index, acceptance = next(pmo.glob("485_WBS*")), next(pmo.glob("486_WBS*"))
old, old_acceptance = index.read_bytes(), acceptance.read_bytes()
assigned, = (row for row in json.loads(old)["artifacts"] if row["path"] == dao["path"])
assert assigned["owner"] == assigned["costOwner"] == "WBS-P004-03"
entry = dict(
    testId=test_id, traceOwner="WBS-G08", owner=assigned["owner"], costOwner=assigned["costOwner"],
    production=dao, source=core, requirementIds=["DAT-009", "OPS-009"],
    design=["UI251", "SS331 §3.12", "SS332 SSC063/448/461"], fixture=unit["fixture"],
    independentOracle=unit["independentOracle"], unit=unit_ref, style=style_ref, historicalEight=lineage_ref,
    newRuns=0, historicalTestsCombined=0, originalRowPriceCountedPp=0,
    unresolved=["P004-03 actual DAO DB role and committed postconditions",
                "actual original ownership and retirement", "current source whole 451"], formalDelta=0)
key = "currentReferenceDaoCombinedFailureTracePG40918"
new = append(old, key, entry)
old_sha = digest(old)
assert json.loads(old_acceptance)["inventorySha256"] == old_sha and old_acceptance.count(old_sha.encode()) == 1
new_acceptance = append(old_acceptance.replace(old_sha.encode(), digest(new).encode()), key, entry)
out = Path(unit_ref["path"]).parent.parent / ctx["run"]
out.mkdir()
index.write_bytes(new)
acceptance.write_bytes(new_acceptance)
(out / "manifest.json").write_text(json.dumps(
    dict(actualExit=0, startEvent=group["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
         trace=entry, inventory=pin(index), acceptance=pin(acceptance)),
    indent=2, ensure_ascii=False) + "\n")
