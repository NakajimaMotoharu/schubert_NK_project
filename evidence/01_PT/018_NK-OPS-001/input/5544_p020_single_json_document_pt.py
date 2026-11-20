"""Run single-document validation against the prior admitted comparison fixture."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PROJECT = Path("program/characterization")
JAVA = Path("dev/codex/schubert/characterization")
OWNER = "dev.codex.schubert.characterization.GateSyntheticRunPortTest"
METHOD = "requiredEvidenceContainsExactlyOneJsonDocument"
MAIN = PROJECT / "src/main/java" / JAVA / "GateContractValidator.java"
TEST = PROJECT / "tests/java" / JAVA / "GateSyntheticRunPortTest.java"


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return {"path": str(path), "sha256": sha256(path.read_bytes()).hexdigest()}


def write(path, value):
    with path.open("x") as output:
        output.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def fingerprint_classes(root):
    return {str(path.relative_to(root)): pin(path)["sha256"] for path in root.rglob("*.class")}


def main(phase):
    assert phase in ("red", "green")
    red = phase == "red"
    plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1455_*.json"))
    group = json.loads(plan.read_bytes())
    values = group["values"]
    originals = values["oracleReferences"][1:]
    assert all(pin(Path(row["path"])) == row for row in originals)
    old, fixture, independent = [json.loads(Path(ref["path"]).read_bytes()) for ref in originals]
    assert old["source"] == fixture["source"] == independent["toolSource"]
    assert old["expected"] == fixture["expected"] == 210
    assert old["stages"]["unit"]["actualExit"] == 0 and independent["actualExit"] == 0
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    changes = {TEST} if red else {MAIN, TEST}
    names = subprocess.check_output(
        ["git", "diff", "--name-only", old["source"], current, "--", PROJECT], text=True)
    assert {Path(path) for path in names.splitlines()} == changes
    baseline = PROJECT / "baseline/current"
    tree = subprocess.check_output(["git", "rev-parse", f"{current}:{baseline}"], text=True).strip()
    assert tree == subprocess.check_output(["git", "rev-parse", f"{old['source']}:{baseline}"], text=True).strip()
    run_name = values["run"] if red else "PG40998-p020-gate-single-json-doc-green-v1"
    work = Path("../pgpt-runs/PG379").resolve() / run_name
    work.mkdir(mode=0o700)
    snapshot = work / "snapshot"
    old_snapshot = Path(fixture["snapshot"])
    inputs = {}
    for name, digest in fixture["inputHashes"].items():
        path = Path(name)
        assert path == Path("pom.xml") or path.is_relative_to(PROJECT)
        old_file = old_snapshot / path
        assert pin(old_file)["sha256"] == digest
        destination = snapshot / path
        destination.parent.mkdir(exist_ok=True, parents=True)
        if path in changes:
            destination.write_bytes(subprocess.check_output(["git", "show", f"{current}:{name}"]))
        else:
            shutil.copyfile(old_file, destination)
        inputs[name] = pin(destination)["sha256"]
    assert {name for name in inputs if inputs[name] != fixture["inputHashes"][name]} == set(map(str, changes))
    assert len([p for p in inputs if p.startswith(str(baseline) + "/")]) == 27

    java, javac = Path(fixture["java"]["path"]), Path(fixture["javac"]["path"])
    assert pin(java) == fixture["java"] and pin(javac) == fixture["javac"]
    sdk = {name: Path(item["path"]) for name, item in fixture["tools"].items()}
    assert all(pin(path) == fixture["tools"][k] for k, path in sdk.items())
    tc = Path("../toolchain").resolve()
    env = {"JAVA_HOME": str(java.parents[1]), "PATH": f"{java.parent}:{os.defpath}",
           "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    steps = []

    def run(label, argv, allowed=(0,)):
        command = list(map(str, argv))
        started = utc()
        result = subprocess.run(command, cwd=work, env=env, capture_output=True, timeout=120, check=False)
        stdout, stderr = work / (label + ".stdout"), work / (label + ".stderr")
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        term = dict(step=label, command=command, exitCode=result.returncode, startedAtUTC=started,
                    terminalAtUTC=utc(), stdout=pin(stdout), stderr=pin(stderr))
        write(work / (label + "-terminal.json"), term)
        steps.append(term)
        if result.returncode not in allowed:
            raise SystemExit(result.returncode)
        return result.stdout

    run("format", [java, "-jar", tc / "google-java-format-1.36.1-all-deps.jar",
                   "--dry-run", "--set-exit-if-changed", *(snapshot / p for p in sorted(changes))])
    if red:
        classes = Path(old["classesDir"])
        assert fingerprint_classes(classes) == old["mainPhysical"]
    else:
        classes = snapshot / PROJECT / "target/classes"
        maven = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
        run("compile-tool", [maven, "-o", "-B", "-ntp", "-N", f"-Dmaven.repo.local={tc}/m2/repository",
                             "-f", snapshot / PROJECT / "pom.xml", "compile"])
    tests, reports, temp = work / "tests", work / "reports", work / "tmp"
    for directory in (tests, reports, temp):
        directory.mkdir(mode=0o700)
    roster = [selector for flag, selector in fixture["selectors"] if flag == "--select-class"]
    assert len(roster) == len(set(roster)) == 20 and OWNER in roster
    cp = ":".join(str(path) for key, path in sdk.items() if "jacoco" not in key)
    inputs_to_compile = (
        [snapshot / TEST] if red else
        [snapshot / PROJECT / "tests/java" / (case.replace(".", "/") + ".java") for case in roster])
    run("compile-test", [javac, "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                         "-cp", f"{classes}:{cp}", "-sourcepath", snapshot / PROJECT / "tests/java",
                         "-d", tests, *inputs_to_compile])
    counts = {}
    stream = work / "unit.exec"
    session = run_name.split("-")[0] + "-SINGLE-JSON-DOCUMENT"
    agent = sdk["org.jacoco.agent-0.8.15-runtime.jar"]
    selection = [("--select-method", OWNER + "#" + METHOD)] if red else [
        ("--select-class", item) for item in roster]
    run("unit", [java, "-Xmx1g", "-Djava.awt.headless=true", "-Duser.language=ja", "-Duser.country=JP",
                 "-Duser.timezone=Asia/Tokyo", f"-Dchr.unitProjectRoot={snapshot}",
                 f"-Djava.io.tmpdir={temp}", f"-javaagent:{agent}=destfile={stream},sessionid={session},append=false",
                 "-jar", sdk["junit-platform-console-standalone-1.13.4.jar"], "execute", "--disable-ansi-colors",
                 "--fail-if-no-tests", "--class-path", f"{classes}:{tests}:{snapshot/PROJECT/'tests/resources'}:{cp}",
                 "--reports-dir", reports, "--config=junit.jupiter.execution.parallel.enabled=false",
                 *(item for pair in selection for item in pair)], allowed=((0, 1) if red else (0,)))
    xml = reports / "TEST-junit-jupiter.xml"
    report = ET.parse(xml).getroot()
    counts = {key: int(report.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    target, = [row for row in report.findall("testcase") if row.attrib["name"] == METHOD + "()"]
    assert target.attrib["classname"] == OWNER
    out = OPS / run_name
    out.mkdir()
    if red:
        failure = target.find("failure")
        assert failure is not None and "nothing was thrown" in failure.attrib["message"]
        assert counts == dict(tests=1, failures=1, errors=0, skipped=0)
        raw = None
        actual = None
    else:
        assert counts == dict(tests=211, failures=0, errors=0, skipped=0)
        previous_xml = Path(independent["legacyRoster"]["path"])
        assert pin(previous_xml) == independent["legacyRoster"]
        before_cases = Counter((row.attrib["classname"], row.attrib["name"])
                               for row in ET.parse(previous_xml).getroot().findall("testcase"))
        after_cases = Counter((row.attrib["classname"], row.attrib["name"]) for row in report.findall("testcase"))
        assert after_cases == before_cases + Counter({(OWNER, METHOD + "()"): 1})
        physical = sorted(classes.rglob("*.class"))
        assert len(physical) == len(old["mainPhysical"]) == 17
        raw_path = out / "unfiltered.tsv"
        table = run("unfiltered", [*independent["rawCommand"][:4], stream, *physical])
        raw_path.write_bytes(table)
        raw = pin(raw_path)
        actual = {}
        for line in table.decode().splitlines():
            row = line.split("\t")
            if row[0] == "CLASS":
                actual[row[1]] = dict(crc64=row[2], crcMatched=row[3] == "true",
                                      counters={key: dict(missed=int(miss), covered=int(covered))
                                                for key, miss, covered in (x.split(":") for x in row[6:])})
    assert all(pin(snapshot / name)["sha256"] == digest for name, digest in inputs.items())
    write(out / "manifest.json", dict(
        source=current, productionCore=values["productionCoreMain"], startEvent=group["eventId"],
        run=run_name, phase=phase, testId="PT-CHR-SYN007", terminalAtUTC=utc(), os="Linux", java="25.0.4",
        testExit=next(step["exitCode"] for step in steps if step["step"] == "unit"),
        expectedResultObserved=True, testCounts=counts, original=originals, inputSha256=inputs,
        unchangedCurrentTree=tree, syntheticFixtureOnly=True, classScopeCount=len(fingerprint_classes(classes)),
        xml=pin(xml), execData=pin(stream), session=session, steps=steps, physical=fingerprint_classes(classes),
        raw=raw, counters=actual, actualProductTests=0, actualBrowserOrChr=0, whole451=False, formalDelta=0))
    print(phase, counts)


if __name__ == "__main__":
    from collections import Counter

    main(sys.argv[1])
