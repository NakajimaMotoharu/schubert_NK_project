"""Check selected JVM-only guard and writer fixtures against the pinned dependencies."""

import argparse
import os
from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET


SUPPORT = runpy.run_path(str(Path(__file__).with_name("5794_f03_scr013_fixture_quality.py")))
ROOT, RUNS, OPS, RECORDS, JAVA = (SUPPORT[k] for k in ("ROOT", "RUNS", "OPS", "RECORDS", "JAVA"))
get, pin, git, now, put, manifest = (SUPPORT[k] for k in ("get", "pin", "git", "now", "put", "manifest"))
OLD_INVOKE = SUPPORT["STAGE_TEMPLATE"]
BASE = Path("src/schubert-nk-api/src")
PACKAGES = "dev/codex/schubert/nk/api/messaging"
PRODUCTS = ("guard/GuardedJmsMessage", "guard/JmsMessageGuard", "outbound/FatalDlqMetadata",
            "outbound/FatalDlqMessageWriter")
PHYSICALS = (*PRODUCTS, "outbound/FatalDlqMetadata$DetectedBy")
TESTS = ("guard/JmsMessageGuardTest", "outbound/FatalDlqMessageWriterTest")
RUN_BEFORE = "PG43200-p00503-jms-guard-dlq-local-quality-v1"
RUN_AFTER = "PG43202-p00503-jms-guard-dlq-exact12-v1"


def main(corrected):
    point, = RECORDS.glob("3470_*")
    start = get(point)["values"]
    core = start["productionCoreMain"]
    source = git("rev-parse", "HEAD").decode().strip()
    mains = [BASE / "main/java" / PACKAGES / (path + ".java") for path in PRODUCTS]
    tests = [BASE / "test/java" / PACKAGES / (path + ".java") for path in TESTS]
    for path in mains:
        assert path.read_bytes() == git("show", f"{core}:{path}") == git("show", f"{source}:{path}")
    for path in tests:
        assert path.read_bytes() == git("show", f"{source}:{path}")
        assert (path.read_bytes() == git("show", f'{start["source"]}:{path}')) != corrected
    original_path, original = manifest("PG26594")
    original_result, cohort = manifest("PG26600")
    assert original["actualExit"] == cohort["actualExit"] == 0 and cohort["tests"] == 170
    names = [PACKAGES.replace("/", ".") + "." + path.replace("/", ".") for path in TESTS]
    expected = sorted((v["classname"], v["name"]) for v in original["expectedCases"]
                      if v["classname"] in names)
    assert len(expected) == len(set(expected)) == 12
    for tag in ("PG43040", "PG22568"):
        target, _ = manifest(tag)
        assert all(test.name.encode() not in target.read_bytes() for test in tests)
    protocol_file, previous = manifest("PG43046")
    protocol = previous["currentJar"]
    assert pin(protocol["path"]) == protocol
    assert previous["sameProtocolTree"] == git("rev-parse", f"{core}:src/schubert-nk-protocol").decode().strip()
    deps = [dict(path=x, sha256=digest) for x, digest in original["dependencies"].items()
            if not Path(x).name.startswith("schubert-nk-protocol-")]
    assert len(deps) == 10 and all(pin(x["path"]) == x for x in deps)
    mode = RUN_AFTER if corrected else RUN_BEFORE
    out = RUNS / mode
    out.mkdir(mode=0o700)
    classes, fixture = out / "target/classes", out / "test"
    for path in (classes, fixture, out / "meter", out / "xml"):
        path.mkdir(parents=True)
    prior = get(RUNS / OLD_INVOKE / "begin.json")["stages"]
    sdk = os.pathsep.join(x["path"] for x in [protocol, *deps])
    cp = os.pathsep.join((str(classes), sdk))
    javac = [str(JAVA / "javac"), "--release", "25", "-encoding", "UTF-8", "-g", "-Xlint:all",
             "-Werror", "-proc:none", "-implicit:none"]
    stages = dict(format=[*prior["format"][:-2], *map(str, tests)],
                  main=[*javac, "-cp", sdk, "-d", str(classes), *map(str, mains)],
                  fixtures=[*javac, "-cp", cp, "-d", str(fixture), *map(str, tests)])
    for stage in ("style", "spotbugs", "pmd", "junit", "rawCompile", "unfiltered"):
        if not corrected and stage in ("junit", "rawCompile", "unfiltered"):
            continue
        args = [x.replace(OLD_INVOKE, mode) for x in prior[stage]]
        if stage == "style":
            args = [*args[:-2], *map(str, tests)]
        if stage == "spotbugs":
            args[args.index("-auxclasspath") + 1] = cp
            del args[-2]
        if stage == "pmd":
            args[args.index("--aux-classpath") + 1] = cp
        if stage == "junit":
            args[args.index("-cp") + 1] = os.pathsep.join((str(fixture), cp))
            args = [*args[:-2], *(item for name in names for item in ("--select-class", name))]
        if stage == "unfiltered":
            args = [*args[:-1], *(str(p) for p in sorted(
                classes / PACKAGES / (name + ".class") for name in PHYSICALS))]
        stages[stage] = args
    (out / "current-static-sources.txt").write_text("".join(f"{x}\n" for x in tests))
    put(out / "begin.json", dict(run=mode, source=source, productCore=core, startedAtUTC=now(),
        sources=list(map(pin, mains + tests)), dependencies=[protocol, *deps],
        original=[pin(original_path), pin(original_result), pin(protocol_file)],
        expectedCases=expected, commands=stages))
    exits = {}
    for stage, cmd in stages.items():
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=120, check=False)
        (out / f"{stage}.stdout").write_bytes(result.stdout)
        (out / f"{stage}.stderr").write_bytes(result.stderr)
        exits[stage] = result.returncode
        print(stage, result.returncode, flush=True)
        assert result.returncode in {"pmd": {0, 4}, "spotbugs": {0, 1}}.get(stage, {0}), stage
    spot = ET.parse(out / "spotbugs.xml").getroot()
    assert not spot.findall("./Errors/Error") and not spot.findall("./Errors/MissingClass")
    warnings = [dict(kind=node.get("type"), method=node.find("Method").get("name")
                     if node.find("Method") is not None else None) for node in spot.findall("BugInstance")]
    pmd = ET.parse(out / "pmd.xml")
    violations = [(x.get("rule"), int(x.get("beginline"))) for x in pmd.findall(".//{*}violation")]
    cases, results = [], []
    if corrected:
        xml = out / "xml/TEST-junit-jupiter.xml"
        suite = ET.parse(xml).getroot()
        assert suite.get("tests") == "12" and all(suite.get(k) == "0" for k in ("failures", "errors", "skipped"))
        cases = sorted((x.get("classname"), x.get("name")) for x in suite.findall("testcase"))
        assert cases == expected
        results = list(map(pin, (xml, out / "unfiltered.stdout", out / "unit.exec")))
    put(out / "terminal.json", dict(run=mode, source=source, productCore=core, terminalAtUTC=now(),
        actualExit=0, stages=exits, results=results, cases=cases, warnings=warnings, pmd=violations,
        physical=[dict(className=p.relative_to(classes).as_posix(), sha256=pin(p)["sha256"])
                  for p in sorted(classes.rglob("*.class"))],
        actualBrokerOperated=False, externalActions=0))
    print(len(cases), "scoped SpotBugs", warnings, "raw PMD", len(violations))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrected", action="store_true")
    main(parser.parse_args().corrected)
