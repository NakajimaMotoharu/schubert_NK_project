"""Verify the approved schema history fixture with in-memory JDBC proxies only."""

import argparse
from hashlib import sha256
import os
from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile


HELPER = runpy.run_path(str(Path(__file__).with_name("5780_p002_portable_reply_envelope.py")))
ROOT, RUNS, OPS, RECORDS, JAVA = (HELPER[k] for k in ("ROOT", "RUNS", "OPS", "RECORDS", "JAVA"))
get, pin, git, now, put = (HELPER[k] for k in ("get", "pin", "git", "now", "begin_file"))
FIXTURE = Path("src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/SchemaHistoryAdmissionTest.java")
MAIN = Path("src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission.java")
TARGETS = ("SchemaHistoryAdmission", "SchemaHistoryAdmission$Row")
BOOTSTRAP = (*TARGETS, "JdbcAdmissionFailures", "JdbcFailureGraph")
STORAGE = ("StorageIoException", "StorageIoException$Reason", "package-info")
STAGES_SOURCE = "PG43130-f03-reply-factory-enum-current-v2"
ISSUE = "THROWS_METHOD_THROWS_CLAUSE_BASIC_EXCEPTION"


def public_receipt(prefix):
    evidence, = OPS.glob(prefix + "*/manifest.json")
    return evidence, get(evidence)


def extract_named(classes, artifacts, module, package, types):
    receipt = artifacts[module]["jar"]
    assert pin(receipt["path"]) == receipt
    result = []
    with ZipFile(receipt["path"]) as archive:
        for name in types:
            member = f"dev/codex/schubert/nk/{package}/{name}.class"
            output = classes / member
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(archive.read(member))
            result.append(dict(className=member, sha256=pin(output)["sha256"]))
    return result


def main(corrected):
    point, = RECORDS.glob("3448_*")
    start = get(point)["values"]
    core = start["productionCoreMain"]
    current = git("rev-parse", "HEAD").decode().strip()
    assert MAIN.read_bytes() == git("show", f"{core}:{MAIN}")
    source = FIXTURE.read_bytes()
    assert source == git("show", f"{current}:{FIXTURE}")
    unchanged = source == git("show", f'{start["source"]}:{FIXTURE}')
    assert unchanged != corrected
    run = ("PG43176-f03-schema-history-fixture-exact13-v1" if corrected else start["run"].replace("-v1", "-v2"))
    receipt, artifacts = public_receipt("PG43066")
    assert artifacts["productCore"] == core
    config, retained = public_receipt("PG43118")
    dependencies = [x for x in retained["classpath"] if Path(x["path"]).name.startswith(
        ("jspecify-", "junit-platform-console-standalone-"))]
    dep_ref, metadata = public_receipt("PG33674")
    jsr, = (x for x in metadata["dependencies"] if Path(x).name.startswith("jsr305-"))
    dependencies.append(dict(path=jsr, sha256=metadata["dependencies"][jsr]))
    assert len(dependencies) == 3 and all(pin(x["path"]) == x for x in dependencies)
    folder = RUNS / run
    folder.mkdir(mode=0o700)
    classes, tests = folder / "target/classes", folder / "test"
    for directory in (classes, tests, folder / "xml", folder / "meter"):
        directory.mkdir(parents=True)
    anchors = extract_named(classes, artifacts["normalArtifacts"], "bootstrap", "api/bootstrap", BOOTSTRAP)
    anchors += extract_named(classes, artifacts["normalArtifacts"], "storage", "storage", STORAGE)
    prior = RUNS / STAGES_SOURCE
    previous = get(prior / "begin.json")["stages"]
    cp = os.pathsep.join([str(classes), *(x["path"] for x in dependencies)])
    steps = {}
    initial_format = None
    if corrected:
        steps["format"] = [*previous["format"][:-2], str(FIXTURE)]
    else:
        initial = RUNS / start["run"]
        first = get(initial / "begin.json")
        stdout = initial / "format.stdout"
        assert first["fixture"] == pin(FIXTURE) and stdout.read_text().strip() == str(FIXTURE)
        assert not (initial / "fixture.stdout").exists()
        initial_format = dict(actualExit=1, begin=pin(initial / "begin.json"), result=pin(stdout))
    steps["fixture"] = [str(JAVA / "javac"), "--release", "25", "-g", "-Xlint:all", "-Werror",
                        "-proc:none", "-implicit:none", "-cp", cp, "-d", str(tests), str(FIXTURE)]
    if corrected:
        agent = next(x.split("=", 1)[0] for x in previous["junit"] if x.startswith("-javaagent:"))
        steps["junit"] = [
            str(JAVA / "java"), "-Dfile.encoding=UTF-8", "-Duser.timezone=Asia/Tokyo",
            "-Djunit.jupiter.extensions.autodetection.enabled=false",
            "-Djunit.jupiter.execution.parallel.enabled=false", "-Djunit.jupiter.execution.timeout.default=30 s",
            f"{agent}=destfile={folder / 'unit.exec'},append=false,sessionid={run}",
            "-cp", os.pathsep.join((str(tests), cp)),
            "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-ansi-colors",
            "--fail-if-no-tests", "--reports-dir", str(folder / "xml"),
            "--select-class", "dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest",
        ]
    for name in ("style", "spotbugs", "pmd", "rawCompile", "unfiltered"):
        if not corrected and name in ("rawCompile", "unfiltered"):
            continue
        step = [x.replace(str(prior), str(folder)) for x in previous[name]]
        if name == "style":
            step = [*step[:-2], str(FIXTURE)]
        if name == "spotbugs":
            step[step.index("-auxclasspath") + 1] = cp
            del step[-2]
        if name == "pmd":
            step[step.index("--aux-classpath") + 1] = cp
        if name == "unfiltered":
            step = [*step[:-1], *(str(classes / "dev/codex/schubert/nk/api/bootstrap" / (x + ".class"))
                                 for x in TARGETS)]
        steps[name] = step
    (folder / "current-static-sources.txt").write_text(str(FIXTURE) + "\n")
    put(folder / "begin.json", dict(source=current, productCore=core, run=run, startUTC=now(),
        fixture=pin(FIXTURE), main=pin(MAIN), toolBaseline=pin(prior / "begin.json"),
        bytes=anchors, exactInputs=dependencies, references=list(map(pin, (receipt, config, dep_ref))),
        commands=steps, priorFormatOnly=initial_format))
    status = {}
    for name, argv in steps.items():
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=120, check=False)
        (folder / f"{name}.stdout").write_bytes(result.stdout)
        (folder / f"{name}.stderr").write_bytes(result.stderr)
        status[name] = result.returncode
        print(name, result.returncode, flush=True)
        assert result.returncode in {"spotbugs": {0, 1}, "pmd": {0, 4}}.get(name, {0}), name
    spot = ET.parse(folder / "spotbugs.xml").getroot()
    assert not spot.findall("./Errors/Error") and not spot.findall("./Errors/MissingClass")
    broad = sorted({node.find("Method").get("name") for node in spot.findall("BugInstance")
                    if node.get("type") == ISSUE})
    pmd = ET.parse(folder / "pmd.xml").getroot()
    violations = sorted((node.get("rule"), int(node.get("beginline")))
                        for node in pmd.findall(".//{*}violation"))
    cases = []
    report = {}
    if corrected:
        assert not broad
        xml = folder / "xml/TEST-junit-jupiter.xml"
        suite = ET.parse(xml).getroot()
        assert suite.get("tests") == "13" and all(suite.get(k) == "0" for k in ("failures", "errors", "skipped"))
        cases = sorted(case.get("name") for case in suite.findall("testcase"))
        assert len(cases) == len(set(cases)) == 13 and any(x.startswith("opsSchema014") for x in cases)
        report = dict(xml=pin(xml), execData=pin(folder / "unit.exec"), rawCounters=pin(folder / "unfiltered.stdout"))
    put(folder / "terminal.json", dict(actualExit=0, terminalAtUTC=now(), source=current, run=run,
        productCore=core, stageExits=status, priorFormatOnly=initial_format, cases=cases, report=report, scopePhysical=anchors,
        checkstyleFindings=0, spotBugsRaw=sorted(
            (node.get("type"), node.find("Method").get("name") if node.find("Method") is not None else "")
            for node in spot.findall("BugInstance")), broadCheckedMethods=broad, pmdRaw=violations,
        fixtureHash=sha256(source).hexdigest(), realDbConnections=0, externalActions=0))
    print("broad checked methods", broad, "cases", len(cases), "PMD", len(violations))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrected", action="store_true")
    main(parser.parse_args().corrected)
