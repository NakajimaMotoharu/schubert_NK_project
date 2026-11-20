"""Bind the latest inspection proof and scan only the subsequent published patch range."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import json
import subprocess


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return {"path":str(path),"sha256":digest(path.read_bytes())}


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git",*args],timeout=30)


pmo=Path("documents/400_PGPT/470_PMO")
plan=next(pmo.glob("601_*"))
start=read(next(plan.glob("1259_*")))
ctx=start["values"]
core=ctx["productionCoreMain"]
head=ctx["source"]
assert git("rev-parse","HEAD").decode().strip()==head==git("rev-parse","origin/dev-foundation").decode().strip()
ops=Path("evidence/01_PT/018_NK-OPS-001/evidence")
scan_base_path=next(ops.glob("PG40824-*/manifest.json"))
scan_base=read(scan_base_path)
base=scan_base["source"]
assert scan_base["actualExit"]==scan_base["detected"]==0
assert git("merge-base",base,head).decode().strip()==base
commits=git("rev-list","--reverse",f"{base}..{head}").decode().splitlines()
path_set,patches,patch_notes=set(),[],[]
for commit in commits:
    changed=set(git("diff","--name-only","-z",commit+"^",commit).decode().split("\0")[:-1])
    assert changed and all(p.startswith(("src/","documents/","evidence/")) and "/PG40750-" not in p and "/PG40766-" not in p for p in changed)
    assert all(Path(p).suffix in {".json",".md",".java",".py",".xml",".tsv",".txt"} for p in changed)
    patch=git("diff","--no-ext-diff","--no-renames","--unified=0",commit+"^",commit)
    patch_notes.append(dict(commit=commit,paths=len(changed),sha256=digest(patch)))
    path_set.update(changed)
    patches.append(patch)
patch_bytes=b"\n".join(patches)
scanner=Path("../toolchain/gitleaks-8.30.1-linux-x64/gitleaks")
scan_argv=[str(scanner),"stdin","--redact=100","--no-banner"]
scan=subprocess.run(scan_argv,input=patch_bytes,capture_output=True,timeout=45)
assert scan.returncode==0,"public patch scan requires review"
unit_path=next(ops.glob("PG40842-*/manifest.json"))
unit=read(unit_path)
abi_path=next(ops.glob("PG40844-*/manifest.json"))
abi=read(abi_path)
assert unit["currentCore"]==abi["core"]==core and unit["counts"]=={"passed":13}
names=sorted(c["testId"] for c in unit["cases"] if c["testId"].startswith("INSPPORT"))
assert names==["INSPPORT011","INSPPORT012"]
main=next(item for item in unit["sourceInputs"] if item["path"].endswith("/InspectionSummaryRepository.java"))
test=next(item for item in unit["sourceInputs"] if item["path"].endswith("/InspectionSummaryPortTest.java"))
assert pin(Path(main["path"]))==main and pin(Path(test["path"]))==test
inventory_path=next(pmo.glob("485_WBS*"))
acceptance_path=next(pmo.glob("486_WBS*"))
inventory_before=inventory_path.read_bytes()
acceptance_before=acceptance_path.read_bytes()
inventory=read(inventory_path)
acceptance=read(acceptance_path)
assert acceptance["inventorySha256"]==digest(inventory_before)
old_binding=inventory["currentG08AlarmAndRequestAuditPG40832"]
assert old_binding["newTestsTogether"]==19
owner,=(art for art in inventory["artifacts"] if art["path"]==main["path"])
assert owner["costOwner"] in ("WBS-P004-02","WBS-P017-07")
typed_path=next(ops.glob("PG40838-*/manifest.json"))
row=dict(currentCore=core,unitSource=unit["unitSource"],affectedMain=main,fixture=test,formalOwner=owner["owner"],costOwner=owner["costOwner"],
         testIds=names,localProof=pin(unit_path),abi=pin(abi_path),typed=pin(typed_path),priorProductTestIds=19,
         newTestIdsAdded=2,globalSourceTestsCombined=False,formalDelta=0,related=["BUG-3416","YKT-2359","WBS-P004-02","WBS-P004-05","WBS-F03"],
         realDatabaseEvidence=False,whole451=False)
key="currentInspectionSummaryFailurePG40852"
def add(raw,data):
    assert raw.endswith(b"\n}\n")
    original=json.loads(raw)
    assert key not in original
    payload=json.dumps({key:data},ensure_ascii=False,indent=2).encode()
    updated=raw[:-3]+b",\n"+payload[2:-2]+b"\n}\n"
    post=json.loads(updated)
    assert post.pop(key)==data and post==original
    return updated
after_inventory=add(inventory_before,row)
old_hash=acceptance["inventorySha256"].encode()
assert acceptance_before.count(old_hash)==1
new_hash=digest(after_inventory)
after_acceptance=add(acceptance_before.replace(old_hash,new_hash.encode()),row)
inventory_path.write_bytes(after_inventory)
acceptance_path.write_bytes(after_acceptance)
out=ops/ctx["run"]/"manifest.json"
out.parent.mkdir()
out.write_text(json.dumps(dict(actualExit=0,core=core,src=head,baseExclusive=base,beginEvent=start["eventId"],commitCount=len(commits),
    uniquePublicPaths=len(path_set),patchStreamSHA256=digest(patch_bytes),patchNotes=patch_notes,detected=0,scanArgv=scan_argv,
    scanRawOutputWritten=False,scanTool=pin(scanner),trace=row,inventory=pin(inventory_path),acceptance=pin(acceptance_path),
    protectedArtifactReads=0,heldInputsOpened=0,postedExternalOperations=0,newTestsRun=0,wholeG07=False,whole451=False,formalDelta=0,
    terminalAtUTC=datetime.now(timezone.utc).isoformat()),ensure_ascii=False,indent=2)+"\n")
print(pin(out),len(commits),len(path_set))
