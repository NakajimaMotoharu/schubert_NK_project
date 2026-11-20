"""Pin the newest recorded web error cohorts and their current source limitations."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


pmo = Path("documents/400_PGPT/470_PMO")
start = json.loads(next(pmo.glob("601_*/1352_*")).read_bytes())
ctx = start["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
names = [
    ("A1-33.02", "WBS-P015-02", "InternalErrorDispatchRouter", "ErrorDispatchRouterPortTest", 18),
    ("A1-36.05", "WBS-P016-24", "WebErrorDispatchFilter", "ErrorDispatchRestorePortTest", 22),
]
source = ctx["productionCoreMain"]
cases = []
for ref, (work, owner, name, fixture, original_count) in zip(refs[2:], names, strict=True):
    receipt_path = Path(ref["path"])
    data = json.loads(receipt_path.read_bytes())
    assert data["actualExit"] == 0 and data["tests"] == original_count
    assert data["actualBackendNativeFsRootOrHeldClassActions"] == 0
    assert data["targetFour100"] and not data["whole451Accepted"]
    xml = receipt_path.with_name("original-TEST-junit-jupiter.xml")
    assert pin(xml)["sha256"] == data["files"][xml.name]
    suite = ET.parse(xml).getroot()
    assert int(suite.attrib["tests"]) == original_count
    assert all(int(suite.attrib[field]) == 0 for field in ("failures", "errors", "skipped"))
    selected = [case for case in suite.findall("testcase")
                if case.attrib["classname"].endswith("." + fixture)]
    assert len(selected) == 8 and all(len(case) == 0 or
                                     all(child.tag not in {"failure", "error", "skipped"} for child in case)
                                     for case in selected)
    production, = (path for path in data["inputHashes"] if path.endswith(f"/{name}.java"))
    fixture_source, = (path for path in data["inputHashes"] if path.endswith(f"/{fixture}.java"))
    counters, = (value for binary, value in data["targetCounters"].items() if binary.endswith("/" + name))
    assert all(value["missed"] == 0 for value in counters.values())
    checked = []
    changed = []
    for path, old_sha in data["inputHashes"].items():
        if not path.startswith("src/") or not path.endswith(".java"):
            continue
        commit = source if "/src/main/" in path else ctx["source"]
        payload = subprocess.check_output(["git", "show", f"{commit}:{path}"], timeout=10)
        current_sha = sha(payload)
        checked.append(path)
        if current_sha != old_sha:
            changed.append(dict(path=path, originalSha256=old_sha, currentSha256=current_sha))
    assert production in checked and fixture_source in checked
    assert all(row["path"] not in {production, fixture_source} for row in changed)
    cases.append(dict(
        workId=work, owner=owner, main=production, fixture=fixture_source,
        retainedOriginal=ref, historicalJUnit=pin(xml), historicalCohort=original_count,
        historicalRelevantCaseNames=[case.attrib["name"] for case in selected],
        historicalTargetCounters=counters, verifiedJavaInputCount=len(checked),
        changedJavaInputs=changed, targetMainAndFixtureIdentical=True,
        currentSameRunEvidence=False, currentReleaseOrActualHttpVerified=False))
assert len(cases[0]["changedJavaInputs"]) == 0 and len(cases[0]["historicalRelevantCaseNames"]) == 8
assert len(cases[1]["changedJavaInputs"]) == 14
assert all("src/schubert-nk-protocol/" in row["path"] for row in cases[1]["changedJavaInputs"])
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
result = dict(actualExit=0, source=source, startEvent=start["eventId"],
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), oldIndex=refs[1],
              rows=cases, productTestsRerun=0, totalPriorCasesCountedAsNew=0, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
