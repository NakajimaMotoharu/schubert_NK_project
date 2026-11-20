"""Attach the fixed current-scope evidence while retaining the original WBS counts."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess


def sha(value):
    return sha256(value).hexdigest()


def pin(path):
    return dict(path=str(path),sha256=sha(path.read_bytes()))


def load(pattern, directory):
    path, = directory.glob(pattern)
    return path,json.loads(path.read_bytes())


pmo = Path("documents/400_PGPT/470_PMO")
plan = next(pmo.glob("601_*"))
ops = Path("evidence/01_PT/018_NK-OPS-001/evidence")
start_path,start = load("1232_*", plan)
core = start["values"]["productionCoreMain"]
snapshot = start["values"]["source"]
inventory_path, inventory = load("485_WBS*",pmo)
acceptance_path, acceptance = load("486_WBS*",pmo)
orig_inventory = inventory_path.read_bytes()
orig_acceptance = acceptance_path.read_bytes()
assert acceptance["inventorySha256"] == sha(orig_inventory)
trace_path, trace = load("PG40818-*/manifest.json",ops)
rows = list(trace["addedTestTrace"])
assert trace["productionCore"] == core
new_fixtures = (
    ("PG40826-*-v2/manifest.json","RequestLogDetailsBoundaryTest.java","PT-IDEM-012-JSON","spec","WBS-P018-09",["WBS-P018-10.02/2","WBS-P018-10.03/2"]),
    ("PG40828-*/manifest.json","AlertWindowedInputContractTest.java","PT-TIMED-RECOVERY","fixtureSpec","WBS-P018-09",["WBS-F03/2-1","WBS-C07"]),
)
for pattern,filename,prefix,spec_key,owner,refs in new_fixtures:
    path,record = load(pattern,ops)
    assert record["core"]==core and record["actualExit"]==0
    source, = (item for item in record["sources"] if item["path"].endswith("/"+filename))
    actual = subprocess.check_output(["git","show",f"{snapshot}:{source['path']}"])
    assert sha(actual)==source["sha256"]
    spec = record[spec_key]
    assert pin(Path(spec["path"])) == spec
    cases = [c for c in record["cases"] if c["testId"].startswith(prefix)]
    if filename=="AlertWindowedInputContractTest.java":
        test_ids = sorted(c["testId"] for c in cases if c["owner"]=="AlertWindowedInputContractTest")
        assert len(test_ids)==3
    else:
        test_ids = sorted(c["testId"] for c in cases)
        assert len(test_ids)==2
    assert all(c["outcome"]=="passed" for c in cases)
    rows.append(dict(wbs=owner,sharedWbs=refs,test=source["path"],sha256=source["sha256"],spec=spec,
                     receipt=pin(path),executedCore=core,caseIds=test_ids))
assert len(rows)==6 and len({i for row in rows for i in row["caseIds"]})==19
main_paths = trace["mainSourceStyle"]["changedPaths"]
artifact_by_path = {item["path"]: item for item in inventory["artifacts"]}
owners=[]
for path in main_paths:
    item = artifact_by_path[path]
    if item["costOwner"] not in ("WBS-P018-09","WBS-C07"):
        raise ValueError(f"unexpected unchanged owner for {path}")
    new = subprocess.check_output(["git","show",f"{core}:{path}"])
    owners.append(dict(path=path,sha256=sha(new),owner=item["owner"],costOwner=item["costOwner"],
                       runtimeEvidenceComplete=False))
assert len(owners)==8
records={}
for pat in ("PG40800-*/manifest.json","PG40802-*/manifest.json","PG40818-*/manifest.json",
            "PG40820-*-v2/manifest.json","PG40826-*-v2/manifest.json","PG40828-*/manifest.json","PG40830-*/manifest.json"):
    receipt,v=load(pat,ops)
    assert v["actualExit"]==0
    records[receipt.parent.name.split("-")[0]]=pin(receipt)
p004_old_path,p004_old=load("PG40394-*/manifest.json",ops)
assert p004_old["actualExit"]==0
p004_current_owner_sources=("InspectionSummary.java","InspectionSummaryRepository.java","CleanupCounts.java","BatchRun.java")
p004_current = []
p004_prefix = "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/"
p004_core = p004_old["productionCore"]
for fname in p004_current_owner_sources:
    current = subprocess.check_output(["git","show",f"{core}:{p004_prefix + fname}"])
    old = subprocess.check_output(["git","show",f"{p004_core}:{p004_prefix + fname}"])
    assert current==old
    p004_current.append(dict(path=p004_prefix+fname,sha256=sha(current)))
attachment=dict(productionCore=core,trackedSnapshot=snapshot,caseTrace=rows,mainOwnerByteJoins=owners,records=records,
               currentScopedDistinctCases=189,priorSourceWebByteUnchangedTests=2,currentNewTests=17,newTestsTogether=19,
               currentRequalifiedHistoricalTests=172,unitReplays=0,authoritativeFormalTests=1964,authoritativeFormalScopes=53,
               appliedFull451=False,rawSnapshotLineDeficit=1,heldTestSources=32,closedOriginalDelta=0,effortRate=None,
               p00402StableValueAndSummarySourceEvidence=dict(prior=pin(p004_old_path),sourcePins=p004_current,
                   actualInboxDbAndExactAuthHeld=True,physicalCurrentRunRequalified=False))
key="currentG08AlarmAndRequestAuditPG40832"


def append_object(raw,new_key,value):
    document = json.loads(raw)
    assert new_key not in document
    suffix = b"\n}\n"
    assert raw.endswith(suffix)
    payload = json.dumps({new_key:value},ensure_ascii=False,indent=2).encode()
    result = raw[:-len(suffix)] + b",\n" + payload[2:-2] + suffix
    after = json.loads(result)
    assert after.pop(new_key)==value and after==document
    return result


inventory_after = append_object(orig_inventory,key,attachment)
old_hash=acceptance["inventorySha256"].encode()
new_hash=sha(inventory_after)
assert orig_acceptance.count(old_hash)==1
acceptance_after = append_object(orig_acceptance.replace(old_hash,new_hash.encode()),key,attachment)
assert json.loads(acceptance_after)["inventorySha256"]==sha(inventory_after)
inventory_path.write_bytes(inventory_after)
acceptance_path.write_bytes(acceptance_after)
out=ops/start["values"]["run"]/"manifest.json"
out.parent.mkdir()
manifest=dict(actualExit=0,startEvent=start["eventId"],core=core,traceAttachment=attachment,
              sourceTableBeforeSha256=sha(orig_inventory),sourceTableAfter=pin(inventory_path),
              acceptanceBeforeSha256=sha(orig_acceptance),acceptanceAfter=pin(acceptance_path),
              fullArtifactCoverageAsserted=False,wholeG08=False,whole451=False,formalDelta=0,
              terminalAtUTC=datetime.now(timezone.utc).isoformat(),runner=pin(Path(__file__)))
out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(pin(out))
