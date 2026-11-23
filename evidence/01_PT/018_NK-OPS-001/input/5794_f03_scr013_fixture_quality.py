"""Check and verify the local SCR013 value fixture without service or media operations."""

import argparse
import os
from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile


BASE = runpy.run_path(str(Path(__file__).with_name("5780_p002_portable_reply_envelope.py")))
ROOT, RUNS, OPS, RECORDS, JAVA = (BASE[n] for n in ("ROOT", "RUNS", "OPS", "RECORDS", "JAVA"))
get, pin, git, now, put = (BASE[n] for n in ("get", "pin", "git", "now", "begin_file"))
TARGET = "dev/codex/schubert/nk/web/view/MusicTrackViewModel.class"
FIXTURE = "MusicTrackPublicContractTest.java"
START = "PG43186-f03-scr013-current-fixture-baseline-v1"
END = "PG43188-f03-scr013-current-six-v1"
STAGE_TEMPLATE = "PG43130-f03-reply-factory-enum-current-v2"


def manifest(prefix):
    path, = OPS.glob(prefix + "*/manifest.json")
    return path, get(path)


def exact_dependencies(original, core):
    _, protocol = manifest("PG43046")
    assert protocol["sameProtocolTree"] == git("rev-parse", f"{core}:src/schubert-nk-protocol").decode().strip()
    current = protocol["currentJar"]
    assert pin(current["path"]) == current
    original_jar = original["currentProtocol"]
    assert pin(original_jar["path"]) == original_jar
    product_dependencies = [
        "header/AuthenticationContext", "layout/media/MusicTrackRecord",
        "layout/media/MusicTrackResponseData", "layout/semantic/DisplayPath",
        "layout/semantic/PairRole", "layout/semantic/UserRole",
    ]
    with ZipFile(original_jar["path"]) as a, ZipFile(current["path"]) as b:
        compared = {}
        for tail in product_dependencies:
            name = "dev/codex/schubert/nk/protocol/" + tail + ".class"
            left, right = a.read(name), b.read(name)
            compared[name] = left == right
    command = next(x["command"] for x in original["terminalReceipts"] if x["step"] == "compile")
    prior_libs = command[command.index("-cp") + 1].split(os.pathsep)
    libs = [pin(path) for path in prior_libs if path != original_jar["path"]]
    assert len(libs) == 4 and set(Path(x["path"]).name for x in libs) == {
        "jspecify-1.0.1.jar", "junit-platform-console-standalone-1.13.4.jar",
        "spring-web-7.0.9.jar", "spring-core-7.0.9.jar",
    }
    web = "src/schubert-nk-web/pom.xml"
    assert git("show", f"{core}:{web}") == git("show", f'{original["productionCore"]}:{web}')
    return [current, *libs], compared


def main(corrected):
    point, = RECORDS.glob("3458_*")
    start = get(point)["values"]
    core = start["productionCoreMain"]
    source = git("rev-parse", "HEAD").decode().strip()
    evidence, original = manifest("PG41500")
    assert original["exitCode"] == 0 and len(original["actualCases"]) == 6
    mains = []
    fixture = None
    source_inputs = []
    for ref in original["verifiedSourceInputs"]:
        artifact = Path(ref["path"])
        assert artifact.read_bytes() == git("show", f"{source}:{artifact}")
        if artifact.name == FIXTURE:
            fixture = artifact
            assert (pin(artifact) == ref) != corrected
        else:
            assert pin(artifact) == ref and artifact.read_bytes() == git("show", f"{core}:{artifact}")
            mains.append(artifact)
        source_inputs.append(pin(artifact))
    assert fixture is not None and len(mains) == 3
    for hold in ("PG22568", "PG43040"):
        policy, _ = manifest(hold)
        assert FIXTURE.encode() not in policy.read_bytes()
    artifacts, protocol_matches = exact_dependencies(original, core)
    run = END if corrected else START
    dst = RUNS / run
    dst.mkdir(mode=0o700)
    classes, test_dir = dst / "target/classes", dst / "test"
    for path in (classes, test_dir, dst / "meter", dst / "xml"):
        path.mkdir(parents=True)
    base = RUNS / STAGE_TEMPLATE
    previous = get(base / "begin.json")["stages"]
    sdk = os.pathsep.join(p["path"] for p in artifacts)
    cp = os.pathsep.join((str(classes), sdk))
    javac = [str(JAVA / "javac"), "--release", "25", "-encoding", "UTF-8", "-g",
             "-Xlint:all", "-Werror", "-proc:none", "-implicit:none"]
    stages = {
        "format": [*previous["format"][:-2], str(fixture)],
        "main": [*javac, "-cp", sdk, "-d", str(classes), *map(str, mains)],
        "fixture": [*javac, "-cp", cp, "-d", str(test_dir), str(fixture)],
    }
    for name in ("style", "spotbugs", "pmd", "rawCompile", "unfiltered", "junit"):
        if not corrected and name in ("rawCompile", "unfiltered", "junit"):
            continue
        step = [x.replace(STAGE_TEMPLATE, run) for x in previous[name]]
        if name == "style":
            step = [*step[:-2], str(fixture)]
        if name == "spotbugs":
            step[step.index("-auxclasspath") + 1] = cp
            del step[-2]
        if name == "pmd":
            step[step.index("--aux-classpath") + 1] = cp
        if name == "unfiltered":
            step[-1] = str(classes / TARGET)
        if name == "junit":
            step[step.index("-cp") + 1] = os.pathsep.join((str(test_dir), cp))
            step[-1] = TARGET.removesuffix("/MusicTrackViewModel.class").replace("/", ".") + "." + fixture.stem
        stages[name] = step
    if corrected:
        stages = {n: stages[n] for n in ("format", "main", "fixture", "style",
                                       "spotbugs", "pmd", "junit", "rawCompile", "unfiltered")}
    (dst / "current-static-sources.txt").write_text(str(fixture) + "\n")
    put(dst / "begin.json", dict(run=run, source=source, productCore=core, startedAtUTC=now(),
                               commands=stages, sourceInputs=source_inputs, priorOracle=pin(evidence),
                               artifacts=artifacts, comparedProtocolDirectTypes=protocol_matches))
    exits = {}
    for name, cmd in stages.items():
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=120, check=False)
        (dst / f"{name}.stdout").write_bytes(result.stdout)
        (dst / f"{name}.stderr").write_bytes(result.stderr)
        exits[name] = result.returncode
        print(name, result.returncode, flush=True)
        allowable = {"spotbugs": {0, 1}, "pmd": {0, 4}, "format": {0} if corrected else {0, 1}}
        assert result.returncode in allowable.get(name, {0}), name
    spot = ET.parse(dst / "spotbugs.xml").getroot()
    assert not spot.findall("./Errors/Error") and not spot.findall("./Errors/MissingClass")
    findings = [dict(kind=x.get("type"),
                     method=x.find("Method").get("name") if x.find("Method") is not None else "")
                for x in spot.findall("BugInstance")]
    findings.sort(key=lambda item: (item["kind"], item["method"]))
    pmd = ET.parse(dst / "pmd.xml")
    violations = [(x.get("rule"), int(x.get("beginline"))) for x in pmd.findall(".//{*}violation")]
    cases = []
    ordinary = {}
    if corrected:
        xml = dst / "xml/TEST-junit-jupiter.xml"
        names = ET.parse(xml).getroot()
        assert names.get("tests") == "6" and all(names.get(k) == "0" for k in ("errors", "failures", "skipped"))
        cases = sorted((x.get("name"), x.get("classname"), "pass") for x in names.findall("testcase"))
        assert [list(x) for x in cases] == sorted(original["actualCases"])
        ordinary = dict(xml=pin(xml), exec=pin(dst / "unit.exec"), unfiltered=pin(dst / "unfiltered.stdout"))
    put(dst / "terminal.json", dict(run=run, source=source, productCore=core, excerpts=ordinary,
                                   terminalAtUTC=now(), actualExit=0, stageExits=exits,
                                   cases=cases, spotBugs=findings, pmd=violations,
                                   physical=pin(classes / TARGET), actualMediaDbOrWebServer=0))
    print("cases", len(cases), "SpotBugs", findings, "pmd", len(violations))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrected", action="store_true")
    main(parser.parse_args().corrected)
