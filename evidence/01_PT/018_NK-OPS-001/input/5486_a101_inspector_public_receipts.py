"""Register two WBS66 candidate rows from public source and their retained receipts."""
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


pmo = Path("documents/400_PGPT/470_PMO")
group = json.loads(next(pmo.glob("601_*/1340_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
contract, metadata, source_proof, review = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:]]
assert all(r["actualExit"] == 0 and r["productTestsExecuted"] == 0
           for r in (contract, metadata, source_proof, review))
assert contract["completedOriginalPreparationWorkIds"] == ["WBS-P004-04/1"]
assert review["scope"] == "ROOT_SOURCE_ONLY_NO_COMPILER_BYTECODE_NULLAWAY_SPOTBUGS_PT_OR_COVERAGE_CREDIT"
plan_root = Path("/home/mini/codex/project1/work/PMO/hourly-monitor/wbs66-20261116")
plan = next(plan_root.glob("58_*/WBS.tsv"))
with plan.open(encoding="utf-8-sig") as stream:
    rows = {row[0]: row for row in csv.reader(stream, delimiter="\t") if row}
owners = json.loads(next(pmo.glob("485_WBS*")).read_bytes())["artifacts"]
owner_by_path = {row["path"]: (row["owner"], row["costOwner"]) for row in owners}
selected = []
specifications = [
    ("A1-01.04", "InspectionRunExecutor", "P00404-ORACLE07", 1.95),
    ("A1-01.05", "InspectorDatabaseConnections", "P00404-ORACLE09", 1.65),
]
for wbs, name, oracle_id, price in specifications:
    path_text, = (field for field in rows[wbs] if field.endswith(f"/{name}.java"))
    assert float(rows[wbs][6]) == price
    assert owner_by_path[path_text] == ("WBS-P004-04",) * 2
    current = pin(Path(path_text))
    archived = subprocess.check_output(["git", "show", f'{ctx["productionCoreMain"]}:{path_text}'],
                                      timeout=10)
    assert hashlib.sha256(archived).hexdigest() == current["sha256"]
    oracle, = (entry for entry in contract["checks"] if entry["id"] == oracle_id)
    assert oracle["artifact"] == path_text
    past_sha = contract["ownedSourceHashes"][path_text]
    changed = past_sha != current["sha256"]
    static = [entry for entry in source_proof["proof"] if entry["path"] == path_text]
    if changed:
        correction, = static
        assert correction["sha256"] == current["sha256"]
        assert correction["normalizedForwardEqualsActual"] and correction["inverseEqualsWholeOriginal"]
    else:
        assert not static
    recorded_test, = (entry for entry in metadata["testMetadata"]
                      if entry["path"].endswith(f"/{name}Test.java"))
    assert recorded_test["qualification"] == "METADATA_ONLY_NOT_RUNTIME_QUALIFIED"
    assert recorded_test["beforeAll"] and not recorded_test["wholeBodyReviewed"]
    current_test = pin(Path(recorded_test["path"]))
    assert current_test["sha256"] == recorded_test["sha256"]
    selected.append(dict(
        wbsWorkId=wbs, owner="WBS-P004-04", costOwner="WBS-P004-04", originalPlanPricePp=price,
        currentMain=current, originalContractMainSha256=past_sha, mainChangedSinceOriginal=changed,
        oracleId=oracle_id, originalTestIds=oracle["testIds"], originalPreparationAlreadyCounted=True,
        staticSourceApplicability="EXACT_RETAINED_CORRECTION_BYTES" if changed else "NO_NEW_STATIC_PROOF",
        testSource=current_test, testDefinitionsMetadataOnly=recorded_test["definitions"],
        testLifecycleRequiresQualification=True, acceptedProductTests=0,
        requiredNextEvidence="Authorized current-source whole Test and independent terminal receipt by Inspector owner",
        currentJudgement="PUBLIC_TRACE_ONLY_AWAITING_CURRENT_RUNTIME_QUALIFICATION"))

out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
result = dict(actualExit=0, plan=pin(plan), source=ctx["productionCoreMain"], startEvent=group["eventId"],
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), receipts=refs[1:], selected=selected,
              productTestsExecuted=0, compileOrStaticExecutions=0, realRuntimeActions=0,
              formalDelta=0, originalRowPriceCompletedPp=0, whole451=False)
(out / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
