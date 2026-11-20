"""Run the admitted local tool suites against the newly packaged comparator."""

from collections import Counter
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile


H = runpy.run_path(str(Path(__file__).with_name("064_current_217_owned.py")))
ROOT, TOOLS, MODULE, WORK, OPS = (H[key] for key in ("ROOT", "TOOLS", "MODULE", "WORK", "OPS"))
dump, git, pin, utc = (H[key] for key in ("dump", "git", "pin", "utc"))
RUN = "PG41280-p020-current-216-local-v1"
SESSION = "PG41280-CHARACTERIZATION-COMPARISON-DEFINITIONS-216"
FILESTORE = "dev.codex.schubert.characterization.GateOwnedFileStoreContract"
NEW = "dev.codex.schubert.characterization.ArtifactComparatorTest"


def reference(path):
    return dict(path=str(path), sha256=pin(path))


def read(path):
    return json.loads(path.read_bytes())


def main():
    start_path, = (ROOT / "documents/400_PGPT/470_PMO").glob("601_*/1682_*.json")
    start = read(start_path)
    v = start["values"]
    assert v["run"] == RUN and git("rev-parse", "HEAD").decode().strip() == v["source"]
    assert all(reference(Path(row["path"])) == row for row in v["oracleReferences"])
    package_path, excluded_path, previous_path = [Path(row["path"]) for row in v["oracleReferences"][1:]]
    package, excluded, previous = [read(path) for path in (package_path, excluded_path, previous_path)]
    assert package["run"] == excluded["run"] == H["RUN"]
    assert excluded["state"] == "CURRENT_ADMISSION_NOT_ESTABLISHED_NO_TRANSFER"
    assert not excluded["capsuleTransferred"] and excluded["terminal"] is None
    assert not git("diff", "--name-only", package["toolSource"], v["source"], "--", str(MODULE), "pom.xml")
    assert not git("diff", "--name-only", v["productionCoreMain"], v["source"], "--", ":(glob)src/**/src/main/**")
    assert package["productionCore"] == v["productionCoreMain"] and len(package["physical"]) == 17
    artifact = Path(package["packagingJar"]["path"])
    assert reference(artifact) == package["packagingJar"]
    packaged_work = WORK / package["run"]
    spec = read(packaged_work / "prepared.json")["spec"]

    work = WORK / RUN
    work.mkdir(mode=0o700)
    snapshot = work / "snapshot"
    for name, expected in spec["files"].items():
        if name.startswith("snapshot/"):
            source = packaged_work / name
            assert pin(source) == expected
            out = work / name
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, out)
    physical = snapshot / MODULE / "target/classes"
    with zipfile.ZipFile(artifact) as jar:
        for binary, expected in package["physical"].items():
            source = Path(package["packagingJar"]["path"]).parent / "classes" / binary
            assert jar.read(binary) == source.read_bytes() and pin(source) == expected
            out = physical / binary
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, out)
    testclasses = work / "tests"
    for name, expected in spec["tests"].items():
        if name == FILESTORE.replace(".", "/") + ".class":
            continue
        source = packaged_work / "tests" / name
        assert pin(source) == expected
        out = testclasses / name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, out)
    assert len(list(testclasses.rglob("*.class"))) == 36

    old_local_path, = OPS.glob("PG41122-*/manifest.json")
    old_local = read(old_local_path)
    old_root = WORK / old_local["run"]
    argv = [arg.replace(str(old_root), str(work))
            for arg in old_local["steps"]["unit"]["command"]]
    with_agent, = [i for i, arg in enumerate(argv) if arg.startswith("-javaagent:")]
    argv[with_agent] = argv[with_agent].split(",sessionid=", 1)[0] + ",sessionid=" + SESSION
    assert str(work / "unit.exec") in argv[with_agent]
    selectors = [arg for i, arg in enumerate(argv) if i and argv[i - 1] == "--select-class"]
    assert len(selectors) == 20 and selectors == [s for s in package["selectors"] if s != FILESTORE]
    (work / "tmp").mkdir()
    (work / "reports").mkdir()
    env = {"JAVA_HOME": str(TOOLS / "jdk-25.0.4"), "PATH": os.defpath,
           "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    started = utc()
    result = subprocess.run(argv, cwd=work, env=env, capture_output=True, check=False, timeout=120)
    (work / "unit.stdout").write_bytes(result.stdout)
    (work / "unit.stderr").write_bytes(result.stderr)
    dump(work / "unit-terminal.json", dict(
        command=argv, startedAtUTC=started, terminalAtUTC=utc(), exitCode=result.returncode,
        stdout=reference(work / "unit.stdout"), stderr=reference(work / "unit.stderr")))
    xml = work / "reports/TEST-junit-jupiter.xml"
    root = ET.parse(xml).getroot()
    frozen = read(Path(previous["normalizedCases"]["path"]))
    assert reference(Path(previous["normalizedCases"]["path"])) == previous["normalizedCases"]
    expected = Counter((row["classname"], row["name"]) for row in frozen if row["classname"] != FILESTORE)
    expected.update((NEW, name + "()") for name in (
        "rejectsUnrecognizedComparisonDefinitionVersions", "rejectsNonArrayComparisonDefinitions"))
    assert sum(expected.values()) == 216
    cases = []
    for test in root.findall("testcase"):
        statuses = [child.tag for child in test if child.tag in ("failure", "error", "skipped")]
        cases.append(dict(classname=test.attrib["classname"], name=test.attrib["name"],
                          outcomes=statuses if statuses else ["pass"]))
    actual = Counter((test["classname"], test["name"]) for test in cases)
    counts = {key: int(root.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    assert actual == expected and set(row["classname"] for row in cases) == set(selectors)
    assert result.returncode == 0 and counts == dict(tests=216, failures=0, errors=0, skipped=0)
    assert all(row["outcomes"] == ["pass"] for row in cases)
    assert all(pin(physical / name) == expected for name, expected in package["physical"].items())

    public = OPS / RUN
    public.mkdir()
    dump(public / "cases.json", cases)
    dump(public / "manifest.json", dict(
        run=RUN, testedSource=v["source"], packagedSource=package["toolSource"],
        productionCore=package["productionCore"], locatedBranch=git("branch", "--show-current").decode().strip(),
        snapshot=str(snapshot), session=SESSION, terminalAtUTC=utc(),
        roster=reference(public / "cases.json"), previousRoster=previous["normalizedCases"],
        counts=counts, exit=result.returncode, excludedOwnedFileStore=1, selectors=selectors,
        unchangedCoreMain=True, jar=package["packagingJar"], actualPhysical=package["physical"],
        exactPackagedClasses=17, completeSeparateExec=True, priorExecMerged=False,
        sourcePreparation=reference(package_path), actualBackendActions=0, actualChr=False, whole451=False,
        formalDelta=0, actual=reference(work / "unit-terminal.json"),
        originalExec=reference(work / "unit.exec"), rawXml=reference(xml)))
    print(RUN, counts, "scopes", len(selectors))


if __name__ == "__main__":
    main()
