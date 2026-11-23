"""Verify ordinary cleanup terminal reads with the existing isolated JDBC proxy fixture."""

import os
from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile


BASE = runpy.run_path(str(Path(__file__).with_name("5795_p00503_jms_proxy_fixture_quality.py")))
ROOT, RUNS, RECORDS, JAVA = (BASE[k] for k in ("ROOT", "RUNS", "RECORDS", "JAVA"))
get, pin, git, now, put, manifest = (BASE[k] for k in ("get", "pin", "git", "now", "put", "manifest"))
RUN = "PG43206-a12105-terminal-jdbc-local-baseline-v1"
TEST_ROOT = Path("src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository")
FIXTURE = TEST_ROOT / "CleanupTerminalReferencesJdbcGraphTest.java"
SELECTED = "dev.codex.schubert.nk.batch.repository.CleanupTerminalReferencesJdbcGraphTest"
ADDITIONAL = {
    "ordinaryTerminalReadPreservesTheOriginalFatalErrorAfterClosingItsStatement()",
    "ordinaryTerminalReadReturnsTheFixedDiagnosticWithoutClosingTheBorrowedConnection()",
}
REPOSITORY = "dev/codex/schubert/nk/batch/repository/CleanupTerminalRepository.class"


def main():
    point, = RECORDS.glob("3474_*")
    state = get(point)["values"]
    core = state["productionCoreMain"]
    source = git("rev-parse", "HEAD").decode().strip()
    assert state["run"] == RUN
    original, old = manifest("PG42978")
    current_file, current = manifest("PG43066")
    assert current["productCore"] == core and old["allTargetsAndUseDependencyBytesEqual"]
    assert Path(old["holdFixture"]["path"]).name == "CleanupTerminalRepositoryTest.java"
    assert len(old["physical"]) == 22 and len(old["origTestCases"]) == 2
    template = RUNS / BASE["RUN_AFTER"]
    origin = get(template / "begin.json")
    libs = [p for p in origin["dependencies"] if Path(p["path"]).name.startswith(
        ("jspecify-", "junit-platform-console-standalone-"))]
    assert len(libs) == 2 and all(pin(x["path"]) == x for x in libs)
    assert FIXTURE.read_bytes() == git("show", f"{source}:{FIXTURE}")
    assert FIXTURE.read_bytes() != git("show", f'{state["source"]}:{FIXTURE}')
    out = RUNS / RUN
    out.mkdir(mode=0o700)
    classes, tests = out / "target/classes", out / "test"
    for item in (classes, tests, out / "xml", out / "meter"):
        item.mkdir(parents=True)
    referenced = []
    for module in ("batch", "bootstrap", "storage"):
        archive = current["normalArtifacts"][module]["jar"]
        assert pin(archive["path"]) == archive
        with ZipFile(archive["path"]) as library:
            for member, prior in old["physical"].items():
                if prior["module"] != module:
                    continue
                path = classes / member
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(library.read(member))
                actual = pin(path)["sha256"]
                assert actual == prior["current"], member
                referenced.append(dict(member=member, module=module, sha256=actual))
    assert len(referenced) == len(old["physical"])
    cp = os.pathsep.join([str(classes), *(d["path"] for d in libs)])
    stages = {}
    for name in ("format", "fixtures", "style", "spotbugs", "pmd", "junit", "rawCompile", "unfiltered"):
        command = [word.replace(template.name, RUN) for word in origin["commands"][name]]
        if name in ("format", "style", "fixtures"):
            command = [*command[:-2], str(FIXTURE)]
        if name in ("fixtures", "junit"):
            command[command.index("-cp") + 1] = cp if name == "fixtures" else os.pathsep.join((str(tests), cp))
        if name in ("pmd", "spotbugs"):
            flag = "--aux-classpath" if name == "pmd" else "-auxclasspath"
            command[command.index(flag) + 1] = cp
        if name == "junit":
            command = [*command[:-4], "--select-class", SELECTED]
        if name == "unfiltered":
            command = [*command[:-5], str(classes / REPOSITORY)]
        stages[name] = command
    (out / "current-static-sources.txt").write_text(str(FIXTURE) + "\n")
    put(out / "begin.json", dict(run=RUN, source=source, productCore=core, startedAtUTC=now(), commands=stages,
        fixture=pin(FIXTURE), references=[pin(original), pin(current_file)], physical=referenced,
        scope="ordinary read and former references; all JDBC resources are local proxies"))
    exits = {}
    for name, command in stages.items():
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120, check=False)
        (out / f"{name}.stdout").write_bytes(result.stdout)
        (out / f"{name}.stderr").write_bytes(result.stderr)
        exits[name] = result.returncode
        put(out / f"{name}.exit.json", dict(actualExit=result.returncode, observedAtUTC=now()))
        print(name, result.returncode, flush=True)
        assert result.returncode in {"spotbugs": {0, 1}, "pmd": {0, 4}}.get(name, {0}), name
    xml = out / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    assert suite.get("tests") == "4" and all(suite.get(k) == "0" for k in ("failures", "errors", "skipped"))
    names = {case.get("name") for case in suite.findall("testcase") if case.get("classname") == SELECTED}
    assert names == set(old["origTestCases"]).union(ADDITIONAL)
    spot = ET.parse(out / "spotbugs.xml").getroot()
    assert not spot.findall("./Errors/Error") and not spot.findall("./Errors/MissingClass")
    pmd = ET.parse(out / "pmd.xml")
    put(out / "terminal.json", dict(run=RUN, productCore=core, source=source, actualExit=0, terminalAtUTC=now(),
        testCases=sorted(names), stageExits=exits, spotBugs=[x.get("type") for x in spot.findall("BugInstance")],
        pmd=[x.get("rule") for x in pmd.findall(".//{*}violation")],
        evidence=list(map(pin, (xml, out / "unit.exec", out / "unfiltered.stdout"))),
        actualDbConnections=0, gatedFailedProfileExecuted=False))
    print(len(names), exits)


if __name__ == "__main__":
    main()
