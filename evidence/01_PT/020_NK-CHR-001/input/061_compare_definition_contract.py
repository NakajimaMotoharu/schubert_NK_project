"""Run the fixed comparison-tool suite on a new local read-only source snapshot."""

import hashlib
import json
import os
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TOOLS = ROOT.parent / "toolchain"
MODULE = Path("program/characterization")
PACKAGE = "dev.codex.schubert.characterization"
TEST = MODULE / "tests/java" / PACKAGE.replace(".", "/") / "ArtifactComparatorTest.java"
HELPERS = [TEST.with_name(name + "Test.java") for name in
           ("CorrelatedLogEvidenceValidator", "CorrelatedMenuActionContract")]
FIXTURES = MODULE / "tests/resources/cases"
WORK = ROOT.parent / "pgpt-runs/PG379"
EVIDENCE = ROOT / "evidence/01_PT/020_NK-CHR-001/evidence"
PRIOR_ROSTER = (ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
                / "PG41128-p020-typed-inventory-filestore-independent-v1/case-results.json")
TARGETS = (
    "rejectsUnrecognizedComparisonDefinitionVersions",
    "rejectsNonArrayComparisonDefinitions",
)
CONSTRUCTOR_TEST = "staticToolFactoriesRejectReflectiveConstructionAndRestoreAccess"


def utc():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=20)


def pin(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, record):
    with path.open("x") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
        output.write("\n")


def main(run, mode):
    assert mode in ("red", "green", "qualified")
    head = git("rev-parse", "HEAD").decode().strip()
    work = WORK / run
    work.mkdir(mode=0o700)
    snapshot = work / "snapshot"
    classes = work / "classes"
    classes.mkdir()
    [*sources, _] = git("ls-files", "-z", "--", str(MODULE / "src/main/java")).decode().split("\0")
    fixtures = [FIXTURES / name for name in ("catalog.json", "dif-allowlist.json")]
    java_sources = [*map(Path, sources), TEST, *HELPERS]
    if mode == "qualified":
        java_sources.append(TEST.with_name("CharacterizationIoScopeTest.java"))
    inputs = [*java_sources, *fixtures]
    for path in inputs:
        saved = snapshot / path
        saved.parent.mkdir(parents=True, exist_ok=True)
        committed = git("show", f"{head}:{path}")
        live = (ROOT / path).read_bytes()
        assert live == committed or (mode == "red" and path == TEST), path
        saved.write_bytes(live)

    jdk = TOOLS / "jdk-25.0.4/bin"
    repository = TOOLS / "m2/repository"
    jackson = repository / "com/fasterxml/jackson/core"
    jars = [jackson / name / "2.19.2" / f"{name}-2.19.2.jar"
            for name in ("jackson-annotations", "jackson-core", "jackson-databind")]
    jars += [repository / "org/jspecify/jspecify/1.0.0/jspecify-1.0.0.jar",
             TOOLS / "junit-platform-console-standalone-1.13.4.jar"]
    agent = repository / "org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    steps = {}

    def execute(name, command):
        args = list(map(str, command))
        began = utc()
        result = subprocess.run(args, cwd=work, env=env, capture_output=True, check=False, timeout=120)
        streams = []
        for kind, content in (("stdout", result.stdout), ("stderr", result.stderr)):
            path = work / f"{name}.{kind}"
            path.write_bytes(content)
            streams.append(dict(name=path.name, sha256=pin(path)))
        steps[name] = dict(command=args, beganAtUTC=began, terminalAtUTC=utc(),
                           exitCode=result.returncode, streamDigests=streams)
        dump(work / f"{name}-terminal.json", steps[name])
        return result.returncode

    compile_path = os.pathsep.join(map(str, jars))
    assert execute("javac", [jdk / "javac", "--release", "25", "-Xlint:all", "-Werror", "-encoding",
                             "UTF-8", "-cp", compile_path, "-d", classes,
                             *[snapshot / rel for rel in java_sources]]) == 0
    runtime_path = os.pathsep.join([str(classes), *map(str, jars)])
    full_class = PACKAGE + ".ArtifactComparatorTest"
    (work / "tmp").mkdir()
    selection = (["--select-class", full_class] if mode != "red" else
                 [item for name in TARGETS for item in ("--select-method", full_class + "#" + name)])
    if mode == "qualified":
        selection += ["--select-method", PACKAGE + ".CharacterizationIoScopeTest#" + CONSTRUCTOR_TEST]
    exit_code = execute("junit", [jdk / "java", f"-Dchr.unitProjectRoot={snapshot}",
                                  f"-Djava.io.tmpdir={work / 'tmp'}",
                                  f"-javaagent:{agent}=destfile={work / 'jacoco.exec'}",
                                  "-cp", runtime_path, "org.junit.platform.console.ConsoleLauncher",
                                  "execute", "--disable-ansi-colors", "--disable-banner",
                                  "--details", "summary", "--fail-if-no-tests", *selection,
                                  "--reports-dir", work / "reports"])
    raw = work / "reports/TEST-junit-jupiter.xml"
    root = ET.parse(raw).getroot()
    rows = []
    for case in root.findall("testcase"):
        problems = [dict(kind=child.tag, message=child.attrib.get("message"))
                    for child in case if child.tag in ("failure", "error", "skipped")]
        rows.append(dict(method=case.attrib["name"], issues=problems))
    counts = {key: int(root.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    assert counts["tests"] == len(rows)
    proven_targets = {row["method"].removesuffix("()") for row in rows}
    assert set(TARGETS) <= proven_targets
    if mode == "red":
        assert exit_code == 1 and counts == dict(tests=2, failures=2, errors=0, skipped=0)
        assert all(row["issues"] == [dict(kind="failure", message="expected: <false> but was: <true>")]
                   for row in rows)
    else:
        prior = [item for item in json.loads(PRIOR_ROSTER.read_bytes())
                 if item["classname"] == full_class]
        assert len(prior) == 72 and all(item["outcome"] == "pass" for item in prior)
        expected = {item["name"].removesuffix("()") for item in prior} | set(TARGETS)
        if mode == "qualified":
            expected.add(CONSTRUCTOR_TEST)
        assert exit_code == 0 and counts == dict(tests=len(expected), failures=0, errors=0, skipped=0)
        assert proven_targets == expected
        assert all(not row["issues"] for row in rows)
    assert git("rev-parse", "HEAD").decode().strip() == head
    dest = EVIDENCE / run
    dest.mkdir()
    dump(dest / "cases.json", rows)
    dump(dest / "manifest.json", dict(
        run=run, source=head, branch=git("branch", "--show-current").decode().strip(),
        mode=mode, productionSrcTree=git("rev-parse", f"{head}:src").decode().strip(),
        currentTree=git("rev-parse", f"{head}:{MODULE}/baseline/current").decode().strip(),
        rawXmlSha256=pin(raw), rawExecSha256=pin(work / "jacoco.exec"),
        os=platform.platform(), java="25.0.4", junit="1.13.4", jacoco="0.8.15",
        inputSha256={str(rel): pin(snapshot / rel) for rel in inputs},
        toolSha256={path.name: pin(path) for path in [*jars, agent]},
        physical={str(path.relative_to(classes)): pin(path) for path in sorted(classes.rglob("*.class"))},
        tests=counts, notRun=0, caseResultsSha256=pin(dest / "cases.json"),
        testExit=exit_code, capturedAtUTC=utc(), steps=steps,
        priorRosterSha256=pin(PRIOR_ROSTER),
        currentBaselineReadByTest=False, actualChr=False, formalDelta=0))
    print(json.dumps(dict(run=run, mode=mode, result=counts, testExit=exit_code)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
