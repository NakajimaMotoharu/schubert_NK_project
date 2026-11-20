"""Account for current Java style inputs with existing pinned tool results."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess


def sha(payload):
    return sha256(payload).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


def source_tree(source, scope):
    result = {}
    for entry in git("ls-tree", "-r", "-z", source, "src").split(b"\0"):
        if entry:
            fields, path = entry.decode().split("\t", 1)
            if f"/src/{scope}/java/" in path and path.endswith(".java"):
                result[path] = fields.split()[-1]
    return result


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
start = read(next(plan.glob("1300_*")))
ctx = start["values"]
core = ctx["productionCoreMain"]
head = ctx["source"]
assert git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines() == [head] * 2
assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"])
evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
base_receipt = next(evidence.glob("PG40818-*/manifest.json"))
base = read(base_receipt)
test_base = read(next(plan.glob("1211_*")))["values"]["source"]
base_main = source_tree(base["productionCore"], "main")
current_main = source_tree(core, "main")
before_test, current_test = source_tree(test_base, "test"), source_tree(head, "test")
assert current_main == source_tree(head, "main")
assert base_main.keys() == current_main.keys()
assert before_test.keys() <= current_test.keys()
assert len(base_main) == len(current_main) == base["mainSourceStyle"]["total"] == 1027
assert len(before_test) == base["testSourceCheckstyle"]["total"] == 1149
held = base["testSourceCheckstyle"]["held"]
assert held == 32
assert not git("diff", "--name-only", base["productionCore"], core, "--",
               "pom.xml", ".mvn", "tools/quality/static/checkstyle.xml")
main_delta = {path for path, blob in current_main.items() if base_main[path] != blob}
test_delta = {path for path, blob in current_test.items() if before_test.get(path) != blob}
assert (len(main_delta), len(test_delta), len(current_test)) == (4, 9, 1151)

dataset = ("PG40826-*-v2/manifest.json", "PG40828-*/manifest.json", "PG40842-*/manifest.json",
           "PG40856-*/manifest.json", "PG40858-*/manifest.json", "PG40868-*/manifest.json",
           "PG40874-*/manifest.json", "PG40878-*-after-api/manifest.json",
           "PG40878-*-after-web/manifest.json")
rule_path = "tools/quality/static/checkstyle.xml"
all_rows = {}
for pattern in dataset:
    path = next(evidence.glob(pattern))
    receipt = read(path)
    assert receipt["actualExit"] == 0
    style, formatter = (receipt["steps"][key] for key in ("checkstyle", "format"))
    code_key = "exitCode" if pattern.startswith("PG40842") else "exit"
    assert style[code_key] == formatter[code_key] == 0
    assert any(arg.endswith(rule_path) for arg in style["command"])
    pins = {}
    for group in ("sourceInputs", "sources", "sourceClosure", "productionInputs"):
        for row in receipt.get(group, []):
            pins[row["path"]] = row["sha256"]
    for field in ("fixture", "testInput", "main"):
        if field in receipt:
            item = receipt[field]
            pins[item["path"]] = item["sha256"]
    checked = set(style["command"]) & set(formatter["command"]) & (main_delta | test_delta)
    for candidate in checked:
        snapshot = core if candidate in main_delta else head
        assert candidate not in all_rows
        exact = sha(git("show", f"{snapshot}:{candidate}"))
        assert pins[candidate] == exact and pin(Path(candidate))["sha256"] == exact, (pattern, candidate)
        all_rows[candidate] = dict(path=candidate, sha256=exact, origProof=pin(path),
                                   category="main" if candidate in main_delta else "test")
assert all_rows.keys() == main_delta | test_delta
assert len(test_delta - before_test.keys()) == 2
out = evidence / ctx["run"]
out.mkdir()
manifest = out / "manifest.json"
record = dict(actualExit=0, source=core, testTree=head, previous=pin(base_receipt),
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), startEvent=start["eventId"],
              currentMain=dict(total=1027, existingIdentical=1023, changedEvidence=4, styleFindings=0),
              currentTest=dict(total=1151, previousEligible=1117, priorExistingChanged=7,
                               newFiles=2, eligibleCheckstyle=1119, unresolvedHeld=held),
              exactChanges=sorted(all_rows.values(), key=lambda row: row["path"]),
              priorHeldSourcesOpened=0, formatterReplays=0, checkstyleReplays=0, productTestsRerun=0,
              initialMetadataValidations=["The inspection style receipt uses exitCode.",
                                          "PG40836 repository pin is usable but its fixture predates PG40842."],
              wholeF03=False, whole451=False, formalDelta=0)
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(pin(manifest), record["currentTest"])
