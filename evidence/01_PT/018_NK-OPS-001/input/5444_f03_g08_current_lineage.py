from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess


def git(*args):
    return subprocess.check_output(["git", *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return {"path": str(path), "sha256": digest(path.read_bytes())}


def read(path):
    return json.loads(path.read_bytes())


def one(directory, pattern):
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, (directory, pattern)
    return matches[0]


def sources_at(commit, scope):
    paths = {}
    for row in git("ls-tree", "-r", "-z", commit, "src").split(b"\0"):
        if row:
            meta, path = row.decode().split("\t",1)
            if f"/src/{scope}/java/" in path and path.endswith(".java"):
                paths[path] = meta.split()[-1]
    return paths


def verify_inputs(items, path_set, revision):
    for path in path_set:
        recorded = next(item for item in items if item["path"] == path)
        assert recorded["sha256"] == digest(git("show", f"{revision}:{path}")), path


pt = Path("evidence/01_PT")
batch = pt / "018_NK-OPS-001"
ops = batch / "evidence"
web = pt / "016_NK-WEB-002"
plan = one(Path("documents/400_PGPT/470_PMO"), "601_*")
start_path = one(plan, "1211_*")
start = read(start_path)
core = start["values"]["productionCoreMain"]
snapshot = start["values"]["source"]
old_main_path = one(ops, "PG40762-*/manifest.json")
after_path = one(ops, "PG40798-*-v2/manifest.json")
typed_path = one(ops, "PG40800-*/manifest.json")
old_main = read(old_main_path)
after = read(after_path)
typed = read(typed_path)
old_core = old_main["productionCore"]
assert after["source"] == typed["source"] == core
assert old_main["actualExit"] == old_main["changedCheckstyleErrors"] == 0
main_before, main_after = sources_at(old_core, "main"), sources_at(core, "main")
assert main_before.keys() == main_after.keys()
assert main_after == sources_at(snapshot, "main")
changed = {p for p in main_after if main_before[p] != main_after[p]}
assert len(changed) == 8 and len(main_after) == old_main["currentProductMain"] == 1027
by_module = Counter(p.split("/")[1].removeprefix("schubert-nk-") for p in main_after)
assert by_module == old_main["moduleCounts"]
for gate in ("formatter","checkstyle"):
    step = after["steps"][gate]
    assert step["exit"] == 0 and changed <= set(step["command"])
verify_inputs(after["inputs"], changed, core)
assert not git("diff", "--name-only", old_core, core, "--", "tools/quality/static/checkstyle.xml", "pom.xml")
assert typed["actualExit"] == 0 and typed["compilerControls"]["nullAwayError"]
prior_test_path = one(plan, "1192_*")
prior_test = read(prior_test_path)
prior_test_tree = "d8bdee4cce058368df3f18bd20310f98f0af2559"
test_after = sources_at(snapshot, "test")
assert test_after == sources_at(prior_test_tree, "test")
test_before = sources_at("c4f84ba912da3ea866bdeaffcf53d7a8aa915dae", "test")
assert all(test_after[p] == blob for p, blob in test_before.items())
additions = {p.rsplit("/",1)[-1].removesuffix(".java"):p for p in test_after.keys()-test_before.keys()}
assert len(additions) == 4
assert (len(test_after), prior_test["eligibleTestCheckstyle"]) == (1149,1117)

rows = []
cases_sources = [
    ("ScenarioSearchFormWireTest", "WBS-P016-03", web, "4707_*", one(web/"evidence","PG40792-*/manifest.json"),"PT-SCR003-WIRE-",2,"sourceInputs","checkstyle"),
    ("AsyncQueueRecoveryCompositionTest", "WBS-P018-09", batch, "4740_*", one(ops,"PG40796-*/manifest.json"),"PT-ASYNC-RECOVERY-",2,"sources","checkstyle"),
    ("TimedAlertPendingRecoveryTest", "WBS-P018-09", batch, "4741_*", after_path,"PT-TIMED-RECOVERY-",8,"inputs","checkstyle"),
    ("TimedAlertCriticalRecoveryTest", "WBS-P018-09", batch, "4741_*", one(ops,"PG40804-*/manifest.json"),"PT-TIMED-RECOVERY-",2,"sources","checkstyle"),
]
for test,wbs,root,spec,receipt_path,prefix,expected,input_key,style in cases_sources:
    receipt = read(receipt_path)
    fixture_path = additions[test]
    verify_inputs(receipt[input_key], (fixture_path,), snapshot)
    assert receipt["actualExit"] == receipt["steps"][style]["exit"] == 0
    cases = [c for c in receipt["cases"] if c["testId"].startswith(prefix)]
    assert len(cases) == expected
    assert all(c.get("outcome",c.get("status")) == "passed" for c in cases)
    execution_core = receipt.get("core",receipt.get("sourceCore",receipt.get("source")))
    row = dict(wbs=wbs,spec=pin(one(root,spec)),test=fixture_path,gitBlob=test_after[fixture_path],
               receipt=pin(receipt_path),executedCore=execution_core,caseIds=sorted(c["testId"] for c in cases))
    if test == "ScenarioSearchFormWireTest":
        verify_inputs(receipt["sourceInputs"], (i["path"] for i in receipt["sourceInputs"] if "/main/" in i["path"]), core)
        assert {p:b for p,b in main_before.items() if p.startswith("src/schubert-nk-protocol/")} == {
                   p:b for p,b in main_after.items() if p.startswith("src/schubert-nk-protocol/")}
        protocol_receipt = receipt["protocolReceipt"]
        assert pin(Path(protocol_receipt["path"])) == protocol_receipt
        row["currentScope"] = "Previous run on identical form and Protocol Main input scope; actual HTTP and CHR not performed."
    elif test == "AsyncQueueRecoveryCompositionTest":
        rerun_path = one(ops,"PG40810-*/manifest.json")
        rerun = read(rerun_path)
        assert rerun["core"] == core and rerun["actualExit"] == 0
        verify_inputs(rerun["sources"], (fixture_path,), snapshot)
        current_cases = [item for item in rerun["cases"] if item["owner"]==test]
        assert {i["method"].strip("()") for i in current_cases} == {i["method"].strip("()") for i in cases}
        assert all(c["outcome"] == "passed" for c in current_cases)
        row["currentCoreRequalification"] = pin(rerun_path)
    else:
        assert execution_core == core
        row["bugYkt"] = ["BUG-3415","YKT-2738"]
    rows.append(row)
ids = {i for row in rows for i in row["caseIds"]}
assert len(ids) == 14
runs = [after_path, *(one(ops, f"PG{n}-*-{v}/manifest.json") for n,v in ((40804,"v1"),(40810,"v1"),(40812,"v1"),(40814,"v2"),(40816,"v2")))]
current_successes = []
seen = set()
for path in runs:
    payload = read(path)
    assert payload["actualExit"] == 0 and payload.get("core",payload.get("source")) == core
    assert all(case.get("outcome", case.get("status"))=="passed" for case in payload["cases"])
    case_ids = {c["testId"].strip("()") for c in payload["cases"]}
    assert len(case_ids)==len(payload["cases"]) and seen.isdisjoint(case_ids)
    current_successes.append(dict(receipt=pin(path),qualifiedCases=len(case_ids)))
    seen.update(case_ids)
assert len(seen)==173
result = dict(actualExit=0,frozeAt=snapshot,productionCore=core,previousProductionCore=old_core,
    startedBy=start["eventId"],terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    sixMainByModule=dict(by_module),mainSourceStyle={"unchangedGitBlobs":1019,"changedVerified":8,
      "total":1027,"formatterFindings":0,"checkstyleFindings":0,"changedPaths":sorted(changed)},
    testSourceCheckstyle={"covered":1117,"held":32,"total":1149},addedTestTrace=rows,
    historicalMainStyleReceipt=pin(old_main_path),changedSourceStyleReceipt=pin(after_path),
    typedLocalReceipt=pin(typed_path),testSourceScopeReceipt=pin(prior_test_path),runner=pin(Path(__file__)),
    currentScopedSuccesses=current_successes,currentScopedDistinctCases=173,currentScopedNewCases=12,
    webIdenticalInputHistoricalCases=2,currentCoverageMerged=False,caseIdsTraced=len(ids),
    fullF03=False,whole451=False,formalDelta=0,productTestReplays=0,analyzerReplays=0,heldClassfilesRead=0)
out = ops/start["values"]["run"]/"manifest.json"
out.parent.mkdir()
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(pin(out))
