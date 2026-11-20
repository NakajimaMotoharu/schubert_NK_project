"""Bind existing source style receipts to the current six-module Java inventory."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess


def with_digest(path, data):
    return {"path": str(path), "sha256": sha256(data).hexdigest()}


def pin(path):
    return with_digest(path, path.read_bytes())


def git(*command):
    return subprocess.check_output(["git", *command], timeout=30)


def source_tree(commit):
    tree = {"main": {}, "test": {}}
    for entry in git("ls-tree", "-r", "-z", commit, "src").split(b"\0"):
        if not entry:
            continue
        fields, path = entry.decode().split("\t", 1)
        for kind in tree:
            if f"/src/{kind}/java/" in path and path.endswith(".java"):
                tree[kind][path] = fields.split()[-1]
    return tree


def load_style_record(reference):
    path = Path(reference["path"])
    assert pin(path) == reference
    report = json.loads(path.read_bytes())
    assert report["actualExit"] == 0
    if "formatting" in report:
        checks = [report["formatting"], report["checkstyle"]]
    else:
        steps = report["steps"] if "steps" in report else report["stages"]
        by_name = {(row.get("step") or row.get("stage") or row.get("name")): row for row in steps}
        checks = [by_name["format"], by_name["checkstyle"]]
    formatted, checked = (row["command"] for row in checks)
    assert all(row["exitCode"] == 0 for row in checks)
    assert "--dry-run" in formatted and "--set-exit-if-changed" in formatted
    assert "tools/quality/static/checkstyle.xml" in checked and "-f" in checked
    assert any(arg.endswith("google-java-format-1.36.1-all-deps.jar") for arg in formatted)
    assert any(arg.endswith("checkstyle-14.3.0-all.jar") for arg in checked)
    assert all((path.parent.name not in str(arg)) or not arg.endswith(".java")
               for arg in [*formatted, *checked])
    available = {x["path"]: x for x in report.get("inputs", []) if "path" in x}
    for key in ("main", "fixture", "test"):
        row = report.get(key)
        if isinstance(row, dict) and row.get("path", "").endswith(".java"):
            available[row["path"]] = row
    return available, set(formatted) & set(checked)


def main():
    plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1434_*.json"))
    start = json.loads(plan.read_bytes())
    scope = start["values"]
    core, head = scope["productionCoreMain"], scope["source"]
    repo_head, remote = git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines()
    assert git("merge-base", head, repo_head).decode().strip() == head
    assert git("merge-base", head, remote).decode().strip() == head
    assert not git("diff", "--name-only", head, repo_head, "--", "src", "pom.xml", ".mvn",
                   "tools/quality/static/checkstyle.xml")
    references = scope["oracleReferences"]
    assert all(pin(Path(row["path"])) == row for row in references)
    previous = json.loads(Path(references[1]["path"]).read_bytes())
    assert previous["actualExit"] == 0
    assert not git("diff", "--name-only", previous["source"], core, "--",
                   "pom.xml", ".mvn", "tools/quality/static/checkstyle.xml")
    old_main = source_tree(previous["source"])["main"]
    old_tests = source_tree(previous["testTree"])["test"]
    current = source_tree(head)
    assert source_tree(core)["main"] == current["main"]
    assert old_main.keys() == current["main"].keys()
    assert old_tests.keys() == current["test"].keys()
    main_delta = {p for p, blob in current["main"].items() if old_main[p] != blob}
    test_delta = {p for p, blob in current["test"].items() if old_tests[p] != blob}
    assert (len(main_delta), len(test_delta)) == (4, 7)
    changed = main_delta | test_delta
    matched = {}
    for reference in references[2:-1]:
        pins, inspected = load_style_record(reference)
        for name in sorted(changed & inspected):
            commit = core if name in main_delta else head
            expected = with_digest(name, git("show", f"{commit}:{name}"))
            assert pin(Path(name)) == expected
            if pins.get(name) != expected:
                continue
            item = matched.setdefault(name, dict(**expected, originalProofs=[],
                                                 category="main" if name in main_delta else "test"))
            item["originalProofs"].append(reference)
    assert matched.keys() == changed
    assert len(current["main"]) == previous["currentMain"]["total"] == 1027
    assert len(current["test"]) == previous["currentTest"]["total"] == 1151
    eligible = previous["currentTest"]["eligibleCheckstyle"]
    held = previous["currentTest"]["unresolvedHeld"]
    assert len(current["test"]) == eligible + held and (eligible, held) == (1119, 32)
    counts = {}
    for name in current["main"]:
        module = name.split("/", 2)[1]
        counts[module] = counts.get(module, 0) + 1
    assert len(counts) == 6
    ev = Path("evidence/01_PT/018_NK-OPS-001/evidence") / (scope["run"].removesuffix("-v1") + "-v3")
    ev.mkdir()
    record = dict(actualExit=0, source=core, testTree=head, startEvent=start["eventId"],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), previous=references[1],
                  mainCount=1027, mainUnchangedCount=1023, mainChangedCount=4, mainStyleFindings=0,
                  mainByModule=counts, testCount=1151, testCheckedCount=eligible, heldTestCount=held,
                  exactChanges=list(matched.values()), checkstyleSource=references[-1],
                  toolPriorFailures=[
                      dict(bug="BUG-3437", attempt=1, exitCode=1, analyzerExecutions=0,
                           source="571102a0ec", reason="duplicate style proof"),
                      dict(bug="BUG-3437", attempt=2, exitCode=1, analyzerExecutions=0,
                           reason="command referenced a supplementary source without a source pin")],
                  heldFileContentsRead=0, formatterExecutions=0, checkstyleExecutions=0,
                  productTestsRerun=0, wholeF03=False, whole451=False, formalDelta=0)
    (ev / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(counts, len(matched), eligible, held)


if __name__ == "__main__":
    main()
