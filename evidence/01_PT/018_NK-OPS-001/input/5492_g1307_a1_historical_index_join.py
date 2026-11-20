"""Use the retained proof index to triage WBS66 A1 rows by Git blob identity."""
import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def blobs(commit):
    entries = subprocess.check_output(["git", "ls-tree", "-rz", commit, "--", "src"], timeout=15)
    result = {}
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        header, path = entry.split(b"\t", maxsplit=1)
        _, kind, blob = header.split()
        if kind == b"blob":
            result[path.decode()] = blob.decode()
    return result


pmo = Path("documents/400_PGPT/470_PMO")
group = json.loads(next(pmo.glob("601_*/1349_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
source, post, manual = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:]]
assert source["actualExit"] == post["actualExit"] == manual["actualExit"] == 0
assert post["allOriginalHashSourceExitCountersMatched"]
assert manual["source"] == ctx["productionCoreMain"]
assert manual["lineageMappedAcrossTwoRuns"] == [f"A1-01.0{i}" for i in range(1, 6)]
old_blobs = blobs(source["source"])
new_blobs = blobs(ctx["productionCoreMain"])
historical = {row["path"]: row for row in source["rows"]}
assert len(historical) == source["targetCount"]
inventory = next(pmo.glob("485_WBS*"))
owners = {row["path"]: row["owner"] for row in json.loads(inventory.read_bytes())["artifacts"]}
plan = manual["plan"]
assert pin(Path(plan["path"])) == plan
rows = []
with Path(plan["path"]).open(encoding="utf-8-sig") as stream:
    for item in csv.reader(stream, delimiter="\t"):
        if not item or not item[0].startswith("A1-"):
            continue
        work_id = item[0]
        candidate_paths = [value for value in item if value.startswith("src/") and value.endswith(".java")]
        if not candidate_paths:
            assert item[11].startswith("未特定枠。")
            rows.append(dict(workId=work_id, path=None, currentOwner=None, currentBlob=None,
                             indexSourceBlob=None, state="UNNAMED_ORIGINAL_WBS_SLOT"))
            continue
        path, = candidate_paths
        current = new_blobs.get(path)
        old = old_blobs.get(path)
        proof = historical.get(path)
        owner = owners.get(path)
        if work_id in manual["lineageMappedAcrossTwoRuns"]:
            state = "INDIVIDUAL_PUBLIC_TRACE_EXISTS"
        elif current is None or owner is None:
            state = "CURRENT_PATH_OR_OWNER_UNRESOLVED"
        elif proof is None or not proof["candidates"]:
            state = "NO_CANDIDATE_IN_RETAINED_INDEX"
        elif owner != proof["canonicalOwner"]:
            state = "OWNER_CHANGED_REVIEW_REQUIRED"
        elif current != old:
            state = "MAIN_BLOB_CHANGED_REVIEW_REQUIRED"
        else:
            state = "SAME_MAIN_BLOB_HISTORICAL_CANDIDATE"
        row = dict(workId=work_id, path=path, currentOwner=owner, currentBlob=current,
                   indexSourceBlob=old, state=state)
        if state == "SAME_MAIN_BLOB_HISTORICAL_CANDIDATE":
            row["priorCandidateManifests"] = [
                dict(path=candidate["path"], sha256=candidate["sha256"])
                for candidate in proof["candidates"]]
        rows.append(row)
assert len({row["workId"] for row in rows}) == len(rows) == 209
counts = Counter(row["state"] for row in rows)
assert counts["UNNAMED_ORIGINAL_WBS_SLOT"] == 23
assert counts["INDIVIDUAL_PUBLIC_TRACE_EXISTS"] == 5
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
index = out / "candidate-index.json"
index.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
result = dict(actualExit=0, a1Rows=len(rows), states=dict(counts), source=ctx["productionCoreMain"],
              startEvent=group["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              earlierIndexSource=source["source"], references=refs[1:], plan=plan,
              inventory=pin(inventory), currentIndex=pin(index),
              authorizationsInferred=0, productTestsExecuted=0, sourceFileBodiesOpened=0,
              oldSuccessesReplayed=0, whole451=False, formalDelta=0,
              firstToolAttempt=dict(exitCode=1, cause="Assumed every A1 row had a Java path",
                                    bug="BUG-3424", horizontalReview="YKT-2744"),
              nextJudgment="Each candidate still needs current dependency and class evidence, an independent oracle, allowed input scope and terminal criteria.")
(out / "manifest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
print(dict(counts))
