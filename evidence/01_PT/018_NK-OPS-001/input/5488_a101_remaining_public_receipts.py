"""Complete the A1-01 source-to-work-row mapping with each runtime hold intact."""
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


pmo = Path("documents/400_PGPT/470_PMO")
group = json.loads(next(pmo.glob("601_*/1343_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
contract, metadata, static, review, preparation, inbox, previous = [
    json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:]]
assert all(receipt["actualExit"] == 0 for receipt in (contract, metadata, static, review, preparation, inbox, previous))
assert previous["source"] == ctx["productionCoreMain"]
plan = previous["plan"]
assert pin(Path(plan["path"])) == plan
with Path(plan["path"]).open(encoding="utf-8-sig") as stream:
    rows = {row[0]: row for row in csv.reader(stream, delimiter="\t") if row}
owners = json.loads(next(pmo.glob("485_WBS*")).read_bytes())["artifacts"]
owner_by_path = {row["path"]: (row["owner"], row["costOwner"]) for row in owners}
requirements = [
    ("A1-01.01", "AuthenticationInboxInspector", "WBS-P004-04", "P00404-ORACLE02", 1.65),
    ("A1-01.02", "InboxCleanup", "WBS-P004-02", None, 1.65),
    ("A1-01.03", "InboxResponseInspector", "WBS-P004-04", "P00404-ORACLE03", 1.95),
]
current = []
for wbs, name, owner, oracle_id, price in requirements:
    path, = (value for value in rows[wbs] if value.endswith(f"/{name}.java"))
    assert float(rows[wbs][6]) == price and owner_by_path[path] == (owner, owner)
    blob = subprocess.check_output(["git", "show", f'{ctx["productionCoreMain"]}:{path}'], timeout=10)
    production = pin(Path(path))
    assert hashlib.sha256(blob).hexdigest() == production["sha256"]
    info = dict(wbsWorkId=wbs, owner=owner, originalPricePp=price, production=production,
                acceptedProductTests=0, originalPriceCompletedPp=0)
    if oracle_id is None:
        condition, = (item for item in inbox["criteriaRows"] if item["artifact"] == path)
        assert condition["state"] == "SOURCE_ONLY_HOLD"
        assert preparation["inputHashes"][path] == production["sha256"]
        info.update(originalContract=refs[5], priorCondition=refs[6], matchingOldMain=True,
                    admittedTestIds=[], remaining=condition["remaining"])
    else:
        oracle, = (item for item in contract["checks"] if item["artifact"] == path and item["id"] == oracle_id)
        test, = (item for item in metadata["testMetadata"] if item["path"].endswith(f"/{name}Test.java"))
        test_pin = pin(Path(test["path"]))
        assert test_pin["sha256"] == test["sha256"]
        assert test["qualification"] == "METADATA_ONLY_NOT_RUNTIME_QUALIFIED" and not test["wholeBodyReviewed"]
        exact_original = contract["ownedSourceHashes"][path] == production["sha256"]
        if not exact_original:
            assert review["scope"] == "ROOT_SOURCE_ONLY_NO_COMPILER_BYTECODE_NULLAWAY_SPOTBUGS_PT_OR_COVERAGE_CREDIT"
            repair, = (item for item in static["proof"] if item["path"] == path)
            assert repair["sha256"] == production["sha256"] and repair["inverseEqualsWholeOriginal"]
        info.update(oracleId=oracle_id, originalTestIds=oracle["testIds"], matchingOldMain=exact_original,
                    fixture=test_pin, definitionsMetadataOnly=test["definitions"],
                    testBeforeAllObserved=test["beforeAll"],
                    remaining="Same-source full Test qualification, authorized DB/Inspector evidence and independent postconditions")
    current.append(info)

all_rows = sorted([entry["wbsWorkId"] for entry in current + previous["selected"]])
assert all_rows == [f"A1-01.0{i}" for i in range(1, 6)]
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
result = dict(actualExit=0, startEvent=group["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              source=ctx["productionCoreMain"], plan=plan, retainedReceipts=refs[1:],
              selected=current, lineageMappedAcrossTwoRuns=all_rows, runtimeQualifiedRows=0,
              currentRuntimeActions=0, productTestsExecuted=0, originalRowPriceCompletedPp=0, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
