"""Independently verify the four ExpiryAudit adapter calls and the eight proxy cases."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
TESTS = {"preservesTheFirstFatalFromTheSqlNextChain", "emitsOnlyTheFixedNonfatalDiagnostic"}
ENTRIES = ("SUCCESSFUL", "STAGE", "FINISH", "READ")


def read(path):
    return json.loads(Path(path).read_bytes())


def pin(path):
    return dict(path=str(path), sha256=sha256(Path(path).read_bytes()).hexdigest())


def counters(log, expected):
    classes = set()
    totals = Counter()
    for line in log.read_text().splitlines():
        cols = line.split("\t")
        if cols[0] != "CLASS":
            continue
        name = cols[1] + ".class"
        assert name not in classes
        classes.add(name)
        for field in cols[6:]:
            counter, missed, covered = field.split(":")
            totals[counter, "missed"] += int(missed)
            totals[counter, "covered"] += int(covered)
    assert classes == set(expected)
    return {name: {part: totals[name, part] for part in ("covered", "missed")}
            for name in ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")}


def main():
    old, new = (next(OPS.glob(f"PG40696-*-{mode}/manifest.json")) for mode in ("before", "after"))
    before, after = map(read, (old, new))
    inputs = [old, new]
    for manifest, path in ((before, old), (after, new)):
        assert manifest["actualExit"] == 0 and manifest["actualExternalActions"] == 0
        for stage in manifest["stages"].values():
            assert stage["actualExit"] == 0
            for label in ("stdout", "stderr"):
                assert pin(stage[label]["path"]) == stage[label]
        unit = path.with_name("junit.xml")
        cases = ET.parse(unit).getroot().findall("testcase")
        assert {c.get("name").split("(", 1)[0] for c in cases} == TESTS
        for name in TESTS:
            members = [c for c in cases if c.get("name").startswith(name + "(")]
            assert len(members) == 4
            assert {c.get("name") for c in members} == {
                f"{name}(Entry)[{index}]" for index in range(1, 5)
            }
        console = path.with_name("unit.stdout").read_text()
        assert all(console.count(f"[{index}] {entry} ✔") == 2
                   for index, entry in enumerate(ENTRIES, 1))
        assert len(cases) == 8 and not any(c.findall("*") for c in cases)
        inputs += [unit, path.with_name("jacoco.exec"), path.with_name("unfiltered.stdout")]
    assert before["test"] == after["test"] == pin(after["test"]["path"])
    assert before["pinnedAllowedDependencies"] == after["pinnedAllowedDependencies"]
    assert before["session"] != after["session"]
    assert old.with_name("abi.stdout").read_bytes() == new.with_name("abi.stdout").read_bytes()
    for manifest, receipt, owner in ((before, old, "/storage/StorageIoException"),
                                     (after, new, "/api/bootstrap/JdbcFailureGraph")):
        changed_invokes = [row for row in receipt.with_name("bytecode.stdout").read_text().splitlines()
                           if "invokestatic" in row and ".preserveFatal:" in row]
        assert len(changed_invokes) == 4 and all(owner + ".preserveFatal:" in row for row in changed_invokes)
        assert manifest["physical"].keys() == before["physical"].keys()
    assert sum(before["physical"][key] != after["physical"][key] for key in before["physical"]) == 1
    hit = counters(new.with_name("unfiltered.stdout"), after["physical"])
    assert counters(old.with_name("unfiltered.stdout"), before["physical"]) == hit
    proof = read(next(OPS.glob("PG40660-*/begin.json")))["commands"]
    targets = [after[key]["path"] for key in ("main", "test")]
    out = OPS / "PG40698-f02-expiry-audit-jdbc-independent-v1"
    out.mkdir()
    report = out.resolve() / "checkstyle.xml"
    stages = {}
    for name, cmd in (
        ("format", [*proof["format"][:6], *targets]),
        ("checkstyle", [*proof["checkstyle"][:8], str(report), *targets]),
    ):
        result = subprocess.run(cmd, capture_output=True, check=False, timeout=30)
        logs = {}
        for stream in ("stdout", "stderr"):
            file = out / f"{name}.{stream}"
            file.write_bytes(getattr(result, stream))
            logs[stream] = pin(file)
        stages[name] = dict(command=cmd, actualExit=result.returncode, **logs)
    assert all(v["actualExit"] == 0 for v in stages.values())
    checkstyle = ET.parse(report).getroot()
    assert len(checkstyle.findall("file")) == 2 and not list(checkstyle.iter("error"))
    assert after["main"] == pin(after["main"]["path"])
    (out / "manifest.json").write_text(json.dumps(dict(
        actualExit=0, beforeSource=before["main"], candidateSource=after["main"], test=after["test"],
        baselineCore=before["baselineCore"], oldCallEdges=4, movedCallEdges=4, otherMainChanges=0,
        casesBefore=8, casesAfter=8, newSelectedProductionTests=8, abiEqual=True, liveOwnedJobs=0,
        counters=hit, oldExecMerged=False, commandReceipts=stages, caseIdentities=sorted(TESTS),
        evidence=list(map(pin, [*inputs, report])), whole451=False, formalDelta=0,
        relatedLedgers=["SSC-461", "BUG-3233", "YKT-2680", "BUG-3402", "BUG-3403"],
        independentPostAttempts=[{"actualExit": 1, "stage": "LEGACY_XML_PARAMETER_DISPLAY_NAME"},
                                 {"actualExit": 0, "stage": "XML_INDEX_AND_CONSOLE_DISPLAY"}],
        terminalAtUTC=datetime.now(timezone.utc).isoformat()), indent=2) + "\n")
    print({"callsMoved": 4, "casesBefore": 8, "casesAfter": 8, "coverage": hit})


if __name__ == "__main__":
    main()
