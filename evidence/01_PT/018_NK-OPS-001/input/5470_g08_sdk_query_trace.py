"""Bind each recent PT to its own source, and join only the verified current class bytes."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess


def sha(value):
    return sha256(value).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


def add(raw, key, value):
    assert raw.endswith(b"\n}\n")
    addition = json.dumps({key: value}, ensure_ascii=False, indent=2).encode()
    updated = raw[:-3] + b",\n" + addition[2:-2] + b"\n}\n"
    parsed = json.loads(updated)
    assert parsed.pop(key) == value and parsed == json.loads(raw)
    return updated


pmo = Path("documents/400_PGPT/470_PMO")
group = read(next(pmo.glob("601_*/1294_*")))
ctx = group["values"]
core = ctx["productionCoreMain"]
assert git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines() == [ctx["source"]] * 2
assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"])
e = Path("evidence/01_PT/018_NK-OPS-001/evidence")
typed = next(e.glob("PG40882-*/manifest.json"))
origin = next(e.glob("PG40880-*/public-manifest.json"))
proof = read(typed)
assert proof["core"] == core and proof["actualExit"] == 0 and proof["staticCommandsReplayed"] == 0
physical = {row["classPath"]: row["sha256"] for row in read(origin)["physicalInventory"]}
index = next(pmo.glob("485_WBS*"))
acceptance = next(pmo.glob("486_WBS*"))
before, acceptance_before = index.read_bytes(), acceptance.read_bytes()
owners = {row["path"]: (row["owner"], row["costOwner"]) for row in json.loads(before)["artifacts"]}
rows = []

for binary, detail in sorted(proof["exactTargetByteJoins"].items()):
    pt = detail["ptProof"]
    path = Path(pt["path"])
    assert pin(path) == pt and physical[binary] == detail["classSha256"]
    observed = read(path)
    assert observed["actualExit"] == 0 and len(observed["selectedCases"]) == 17
    assert all(case["outcome"] == "passed" for case in observed["selectedCases"])
    new, = (case for case in observed["selectedCases"] if case["testId"].endswith("017"))
    production, = (row for row in observed["productionInputs"]
                   if row["path"].endswith(binary.removesuffix(".class") + ".java"))
    assert owners[production["path"]] == ("WBS-P018-09",) * 2
    assert pin(Path(production["path"])) == production
    assert sha(git("show", f'{core}:{production["path"]}')) == production["sha256"]
    assert pin(Path(observed["testInput"]["path"])) == observed["testInput"]
    rows.append(dict(testId=new["testId"], owner="WBS-P018-09", costOwner="WBS-P018-09",
                     production=production, fixture=observed["testInput"], spec=observed["specification"],
                     ptRun=pt, ptSource=observed["source"], typedSource=core, typedByteJoin=detail,
                     selectedCohort=17, newInCohort=1, currentSourceCoverageCombined=False))

query_path = next(e.glob("PG40868-*/manifest.json"))
query = read(query_path)
assert query["actualExit"] == 0 and query["caseResults"][0]["testId"] == "CLNQUERY010"
assert query["caseResults"][0]["outcome"] == "passed"
main, = (row for row in query["sourceClosure"] if row["path"].endswith("/CleanupRepository.java"))
assert owners[main["path"]] == ("WBS-P017-07",) * 2
assert all(pin(Path(row["path"])) == row for row in query["sourceClosure"])
assert pin(Path(query["fixture"]["path"])) == query["fixture"]
rows.append(dict(testId="CLNQUERY010", owner="WBS-P017-07", costOwner="WBS-P017-07.01",
                 production=main, fixture=query["fixture"], spec=query["spec"], ptRun=pin(query_path),
                 ptSource=query["core"], currentSourceCoverageCombined=False, typedSource=None,
                 selectedCohort=1, newInCohort=1))

key = "currentStandardSdkOwnerAndCleanupQueryTracePG40884"
entry = dict(core=core, rows=rows, typedProof=pin(typed), publicTypedManifest=pin(origin),
             existingPtEvidenceReused=4, newProductExecutions=0, duplicateCostPricePp=0,
             formalDelta=0, releaseWhole451=False)
new = add(before, key, entry)
old_hash = sha(before)
assert json.loads(acceptance_before)["inventorySha256"] == old_hash
assert acceptance_before.count(old_hash.encode()) == 1
new_acceptance = add(acceptance_before.replace(old_hash.encode(), sha(new).encode()), key, entry)
assert json.loads(new_acceptance)["inventorySha256"] == sha(new)
out = e / ctx["run"]
out.mkdir()
index.write_bytes(new)
acceptance.write_bytes(new_acceptance)
result = dict(actualExit=0, source=core, startEvent=group["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              trace=entry, originalInventorySha256=old_hash, inventory=pin(index), acceptance=pin(acceptance),
              testsRerun=0, analyzersRerun=0, wholeG08=False, formalDelta=0)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(pin(manifest), len(rows))
