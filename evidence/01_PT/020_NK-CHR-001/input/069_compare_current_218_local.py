"""Run the previously admitted 20 local characterization suites on the exact new package."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[4]
MODULE = Path("program/characterization")
WORK = ROOT.parent / "pgpt-runs/PG379"
TOOLS = ROOT.parent / "toolchain"
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
EVIDENCE = ROOT / "evidence/01_PT/020_NK-CHR-001/evidence"
RUN = "PG41344-p020-current-218-local-v1"
TEST = "dev.codex.schubert.characterization.ArtifactComparatorTest"
HELD = "dev.codex.schubert.characterization.GateOwnedFileStoreContract"
NEW_METHODS = ("rejectsCurrentRunCaseReportedAsNkOnly", "rejectsNkOnlyCaseReportedAsCurrentRun")
MUTATED = {"ArtifactComparator.java", "GateContractValidator.java", "ArtifactComparatorTest.java"}
CHANGED_BINARY_NAMES = {"ArtifactComparator.class", "ArtifactComparator$ComparisonResult.class",
                        "GateContractValidator.class", "GateContractValidator$ValidationResult.class"}


def load(path):
    return json.loads(path.read_bytes())


def report(path, data):
    with path.open("x") as output:
        json.dump(data, output, ensure_ascii=False, indent=2)
        output.write("\n")


def digest(raw):
    return sha256(raw).hexdigest()


def pin(path):
    return {"path": str(path), "sha256": digest(path.read_bytes())}


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], cwd=ROOT, timeout=30)


def manifest(base, run):
    document, = base.glob(f"{run}*/manifest.json")
    return document, load(document)


def main():
    current, direct = manifest(EVIDENCE, "PG41342")
    previous, before = manifest(OPS, "PG41280")
    terminal, owner = manifest(OPS, "PG41278")
    original = terminal.with_name("begin.json")
    approved = load(original)
    assert owner["state"] == "CURRENT_ADMISSION_NOT_ESTABLISHED_NO_TRANSFER"
    assert before["packagedSource"] == approved["toolSource"]
    assert not git("diff", "--name-only", direct["source"], "HEAD", "--", MODULE, "pom.xml")
    assert not git("diff", "--name-only", direct["productionCore"], "HEAD", "--", ":(glob)src/**/src/main/**")
    deltas = git("diff", "--name-only", before["packagedSource"], direct["source"], "--", MODULE).decode().splitlines()
    assert {Path(p).name for p in deltas} == MUTATED and len(deltas) == 3
    lived = WORK / approved["run"]
    old_tests = WORK / before["run"]
    spec = load(lived / "prepared.json")["spec"]
    assert len(spec["files"]) == 326 and len(spec["physical"]) == 17
    work = WORK / RUN
    work.mkdir(mode=0o700)
    sources = {}
    for name, expected in spec["files"].items():
        rel = Path(name)
        if rel.parts[0] != "snapshot" or HELD.split(".")[-1] in rel.name:
            continue
        data = (lived / rel).read_bytes()
        assert digest(data) == expected, str(rel)
        path = Path(*rel.parts[1:])
        if str(path) in deltas:
            data = git("show", f"{direct['source']}:{path}")
            assert data == (ROOT / path).read_bytes()
        (work / rel).parent.mkdir(parents=True, exist_ok=True)
        (work / rel).write_bytes(data)
        sources[str(rel)] = digest(data)
    assert {str(Path("snapshot") / name) for name in deltas} <= set(sources)
    assert not any(HELD.split(".")[-1] in key for key in sources)
    package_root = work / "snapshot" / MODULE
    (work / "tmp").mkdir()
    (work / "reports").mkdir()
    env = {"JAVA_HOME": str(TOOLS / "jdk-25.0.4"), "PATH": os.defpath,
           "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    steps = {}

    def execute(stage, argv):
        began = datetime.now(timezone.utc).isoformat()
        done = subprocess.run(argv, cwd=work, env=env, check=False, capture_output=True, timeout=140)
        streams = []
        for kind, body in (("stdout", done.stdout), ("stderr", done.stderr)):
            path = work / (stage + "." + kind)
            path.write_bytes(body)
            streams.append(pin(path))
        info = dict(stage=stage, command=argv, commandExit=done.returncode, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                    beganAtUTC=began, logDigests=streams)
        report(work / (stage + "-terminal.json"), info)
        steps[stage] = info
        assert done.returncode == 0, stage

    build = [a.replace(str(lived), str(work)) for a in load(lived / "package-terminal.json")["argv"]]
    assert "-o" in build and "-Dmaven.test.skip=true" in build and build[-1] == "package"
    execute("package", build)
    artifact, = (package_root / "target").glob("schubert-characterization-*.jar")
    class_root = package_root / "target/classes"
    physical = {str(p.relative_to(class_root)): digest(p.read_bytes()) for p in class_root.rglob("*.class")}
    assert len(physical) == 17 and set(physical) == set(before["actualPhysical"])
    with zipfile.ZipFile(artifact) as file:
        included = [name for name in file.namelist() if name.endswith(".class")]
        assert len(included) == len(set(included)) == len(physical)
        assert {name: digest(file.read(name)) for name in included} == physical
    changed = [name for name in physical if physical[name] != before["actualPhysical"][name]]
    assert {Path(name).name for name in changed} == CHANGED_BINARY_NAMES, changed

    tests = [a.replace(str(lived), str(work)) for a in load(lived / "compile-tests-terminal.json")["argv"]]
    assert not any(HELD.split(".")[-1] in a for a in tests)
    execute("compile-tests", tests)
    assert len(list((work / "tests").rglob("*.class"))) == 36
    assert not list((work / "tests").rglob("*OwnedFileStore*"))
    argv = [a.replace(str(old_tests), str(work)) for a in load(old_tests / "unit-terminal.json")["command"]]
    agent, = [i for i, a in enumerate(argv) if a.startswith("-javaagent:")]
    argv[agent] = argv[agent].split(",sessionid=", 1)[0] + ",sessionid=" + RUN
    selectors = [a for i, a in enumerate(argv) if i and argv[i - 1] == "--select-class"]
    assert selectors == before["selectors"] and len(selectors) == 20 and HELD not in selectors
    execute("junit", argv)
    xml = work / "reports/TEST-junit-jupiter.xml"
    output = ET.parse(xml).getroot()
    roster_file = Path(before["roster"]["path"])
    assert pin(roster_file) == before["roster"]
    expected = Counter((row["classname"], row["name"]) for row in load(roster_file))
    expected.update((TEST, name + "()") for name in NEW_METHODS)
    actual = Counter((r.get("classname"), r.get("name")) for r in output.findall("testcase"))
    totals = {k: int(output.get(k)) for k in ("tests", "failures", "errors", "skipped")}
    assert totals == {"tests": 218, "failures": 0, "errors": 0, "skipped": 0}
    assert expected == actual and set(n[0] for n in actual) == set(selectors)
    assert all(not any(child.tag in ("failure", "error", "skipped") for child in entry)
               for entry in output.findall("testcase"))
    assert all(digest((work / p).read_bytes()) == h for p, h in sources.items())
    public = EVIDENCE / RUN
    public.mkdir()
    report(public / "manifest.json", dict(
        run=RUN, actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        source=direct["source"], productionCore=direct["productionCore"], selectors=selectors,
        testedTests=totals, notRunInDeclaredScope=0, heldFileStore=1,
        independentRosterSha256=pin(roster_file)["sha256"],
        newTests=2, consumedOldTestResultsAsPass=0, package=pin(artifact), physical=physical,
        changedFromEarlierPackage=sorted(changed), originalExec=pin(work / "unit.exec"), originalXml=pin(xml),
        currentBaselineNotChanged=True, originalSnapshotFileHashes=sources,
        steps=steps, relatedProof=[pin(p) for p in (current, previous, original, terminal)],
        firstPreflightExit=1, firstPreflightStage="Wrapper referenced the owned terminal rather than the local package receipt; no build or test started.",
        actualChr=False, actualNewNativeOrNetworkOperations=0, whole451=False, formalDelta=0
    ))
    print(RUN, totals)


if __name__ == "__main__":
    main()
