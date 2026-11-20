"""Connect two measured PTs and a blocked preparation to their original owners."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


def insert(raw, key, value):
    assert raw.endswith(b"\n}\n")
    prospective = json.dumps({key: value}, ensure_ascii=False, indent=2).encode()
    updated = raw[:-3] + b",\n" + prospective[2:-2] + b"\n}\n"
    original, derived = json.loads(raw), json.loads(updated)
    assert key not in original and derived.pop(key) == value and derived == original
    return updated


pmo = Path("documents/400_PGPT/470_PMO")
plan = next(pmo.glob("601_*"))
context = read(next(plan.glob("1275_*")))
values = context["values"]
head = values["source"]
core = values["productionCoreMain"]
assert git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines() == [head, head]
assert all(pin(Path(item["path"])) == item for item in values["oracleReferences"])

inventory = next(pmo.glob("485_WBS*"))
acceptance = next(pmo.glob("486_WBS*"))
inventory_before, acceptance_before = inventory.read_bytes(), acceptance.read_bytes()
inventory_old = json.loads(inventory_before)
locator = {row["path"]: row for row in inventory_old["artifacts"]}
assert len(locator) == len(inventory_old["artifacts"])
results = Path("evidence/01_PT/018_NK-OPS-001/evidence")
rows = []

for prefix, test_id, basename, expected_owner in (
    ("PG40856-", "CLNPORT010", "CleanupStepRepository.java", "WBS-P017-07"),
    ("PG40858-", "EXPPORT-J011", "ExpiryAuditRepository.java", "WBS-P017-11"),
):
    proof = next(results.glob(prefix + "*/manifest.json"))
    run = read(proof)
    main = (next(item for item in run["sourceClosure"] if Path(item["path"]).name == basename)
            if "sourceClosure" in run else run["main"])
    assert run["actualExit"] == 0 and run["core"] == core
    assert len(run["caseResults"]) == 1 and run["caseResults"][0]["testId"] == test_id
    assert run["caseResults"][0]["outcome"] == "passed" and run["testXmlSha256"]
    assert all(step["exit"] == 0 for step in run["steps"].values())
    assert all(pin(Path(item["path"])) == item for item in (main, run["fixture"], run["spec"]))
    assert digest(git("show", f'{core}:{main["path"]}')) == main["sha256"]
    owner = locator[main["path"]]
    assert owner["owner"] == owner["costOwner"] == expected_owner
    rows.append(dict(testId=test_id, owner=expected_owner, costOwner=expected_owner, production=main,
                     fixture=run["fixture"], spec=run["spec"], proof=pin(proof), outcome="LOCAL_PT_PASS",
                     source=core, xmlSha256=run["testXmlSha256"], formalDelta=0))

proof = next(results.glob("PG40860-*/manifest.json"))
hold = read(proof)
main = next(item for item in hold["sourceInputs"] if Path(item["path"]).name == "LogQueryAuditWriter.java")
assert hold["source"] == core and hold["actualExit"] == 1 and hold["stages"]["compile"]["exit"] == 1
assert not hold["qualificationMatched"] and not hold["cases"] and hold["testXmlSha256"] is None
assert pin(Path(main["path"])) == main
owner = locator[main["path"]]
assert owner["owner"] == "WBS-P010-04"
proposal = Path("evidence/01_PT/018_NK-OPS-001/input/5462_log_search_audit_statement_null_proposed.patch")
hold_record = read(next(plan.glob("1274_*")))
assert pin(proposal) in hold_record["outcomeEvidence"]
rows.append(dict(testId="PT-ADM-SEARCHPORT009", owner=owner["owner"], costOwner="WBS-P018-10.03",
                 costSharedWithOwner=False, production=main, proposal=pin(proposal), proof=pin(proof),
                 outcome="NOT_RUN_QA_056_PREREQUISITE", source=core, bug="BUG-3417", expansion="YKT-2739",
                 xmlSha256=None, formalDelta=0))

previous_inventory_hash = digest(inventory_before)
assert json.loads(acceptance_before)["inventorySha256"] == previous_inventory_hash
addition = dict(source=core, originalProductScopeUnchanged=True, rows=rows, measuredLocalPass=2,
                notRun=1, formalDelta=0, newProductExecutions=0, mixedSourceCoverage=False, whole451=False)
key = "currentCleanupExpiryAuditTracePG40864"
update_inventory = insert(inventory_before, key, addition)
new_inventory_hash = digest(update_inventory)
assert acceptance_before.count(previous_inventory_hash.encode()) == 1
update_acceptance = insert(acceptance_before.replace(previous_inventory_hash.encode(),
                                                     new_inventory_hash.encode()), key, addition)
assert json.loads(update_acceptance)["inventorySha256"] == new_inventory_hash
out = results / values["run"]
out.mkdir()
inventory.write_bytes(update_inventory)
acceptance.write_bytes(update_acceptance)
manifest = out / "manifest.json"
record = dict(actualExit=0, startEvent=context["eventId"], head=head,
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), scope=addition,
              previousInventorySha256=previous_inventory_hash, inventory=pin(inventory),
              acceptance=pin(acceptance), wholeG08=False)
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(pin(manifest), len(rows))
