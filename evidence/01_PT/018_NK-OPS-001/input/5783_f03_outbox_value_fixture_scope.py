"""Check and qualify the two standalone Outbox value fixtures; never opens a transport."""

import argparse
import os
from pathlib import Path
import runpy
import subprocess
import xml.etree.ElementTree as ET


PREVIOUS = runpy.run_path(str(Path(__file__).with_name("5780_p002_portable_reply_envelope.py")))
ROOT, RUNS, OPS, RECORDS, API, PKG, JAVA = (PREVIOUS[name] for name in (
    "ROOT", "RUNS", "OPS", "RECORDS", "API", "PKG", "JAVA",
))
get, pin, git, now, begin_file = (PREVIOUS[name] for name in ("get", "pin", "git", "now", "begin_file"))
MAINS = ("OutboxDestination", "OutboxDispatchReport", "OutboxRetrySchedule")
TESTS = ("OutboxValueContractTest", "OutboxDispatchReportBoundaryTest")


def main(corrected):
    point, = RECORDS.glob("3419_*")
    claim = get(point)["values"]
    core, start = claim["productionCoreMain"], claim["source"]
    host_source = git("rev-parse", "HEAD").decode().strip()
    saved, = OPS.glob("PG35363*/manifest.json")
    baseline = get(saved)
    assert baseline["actualExit"] == 0 and baseline["physical5OnlyNoProtocolJar"]
    mains = [API / f"main/java/{PKG}/{name}.java" for name in MAINS]
    tests = [API / f"test/java/{PKG}/{name}.java" for name in TESTS]
    for path in mains + tests:
        payload = path.read_bytes()
        assert payload == git("show", f"{host_source}:{path}")
        old = git("show", f"{start}:{path}")
        if corrected and path == tests[0]:
            assert payload != old
        else:
            assert pin(path)["sha256"] == baseline["inputHashes"][str(path)]
            assert old == payload == git("show", f"{core}:{path}")
    jdk_cp = {p: h for p,h in baseline["dependencies"].items() if Path(p).name.startswith(
        ("jspecify-", "junit-platform-console-standalone-"))}
    assert len(jdk_cp) == 2 and all(pin(p)["sha256"] == h for p,h in jdk_cp.items())
    run = "PG43144-f03-outbox-value-fixture-current-v1" if corrected else claim["run"]
    folder = RUNS / run
    folder.mkdir(mode=0o700)
    classes = folder/"target/classes"
    fixtures = folder/"test"
    for p in (classes, fixtures, folder/"xml", folder/"meter"):
        p.mkdir(parents=True)
    last = RUNS / "PG43130-f03-reply-factory-enum-current-v2"
    known = get(last/"begin.json")["stages"]
    agent = next(x.split("=",1)[0] for x in known["junit"] if x.startswith("-javaagent:"))
    sdk = os.pathsep.join(jdk_cp)
    product_cp = os.pathsep.join((str(classes), sdk))
    javac = [str(JAVA/"javac"), "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none", "-implicit:none"]
    stages = {
        "format": [*known["format"][:-2], *map(str, tests)],
        "main": [*javac, "-cp", sdk, "-d", str(classes), *map(str, mains)],
        "fixture": [*javac, "-cp", product_cp, "-d", str(fixtures), *map(str, tests)],
    }
    if corrected:
        stages["junit"] = [
            str(JAVA/"java"), "-Dfile.encoding=UTF-8", "-Duser.timezone=Asia/Tokyo",
            "-Djunit.jupiter.extensions.autodetection.enabled=false",
            "-Djunit.jupiter.execution.parallel.enabled=false", "-Djunit.jupiter.execution.timeout.default=15 s",
            f"{agent}=destfile={folder/'unit.exec'},append=false,sessionid={run}",
            "-cp", os.pathsep.join((str(fixtures), product_cp)),
            "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-ansi-colors",
            "--fail-if-no-tests", "--reports-dir", str(folder/"xml"),
        ]
        for name in TESTS:
            stages["junit"].extend(("--select-class", f"{PKG.replace('/', '.')}.{name}"))
    for stage in ("rawCompile", "unfiltered", "style", "pmd", "spotbugs"):
        if not corrected and stage not in ("style", "pmd", "spotbugs"):
            continue
        cmd = [arg.replace(str(last), str(folder)) for arg in known[stage]]
        if stage == "unfiltered":
            cmd = [*cmd[:-1], *[str(classes/PKG/(name+".class")) for name in MAINS]]
        if stage == "style":
            cmd = [*cmd[:-2], *map(str, tests)]
        if stage in ("pmd", "spotbugs"):
            marker = "--aux-classpath" if stage == "pmd" else "-auxclasspath"
            cmd[cmd.index(marker)+1] = product_cp
        stages[stage] = cmd
    (folder/"current-static-sources.txt").write_text("".join(f"{s}\n" for s in tests))
    begin_file(folder/"begin.json", dict(source=host_source, productCore=core, startUTC=now(),
        stages=stages, fixtures=list(map(pin,tests)), mainInputs=list(map(pin,mains)), sdk=jdk_cp, original=pin(saved)))
    status = {}
    for key, cmd in stages.items():
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=110, check=False)
        (folder/f"{key}.stdout").write_bytes(proc.stdout)
        (folder/f"{key}.stderr").write_bytes(proc.stderr)
        status[key] = proc.returncode
        print(key, proc.returncode, flush=True)
        assert proc.returncode in {"pmd":{0,4}, "spotbugs":{0,1}}.get(key, {0}), key
        if key == "main":
            output = {p.relative_to(classes).as_posix():pin(p)["sha256"] for p in classes.rglob("*.class")}
            assert output == {f"{PKG}/{name}.class":baseline["physicalClassHashes"][f"{PKG}/{name}.class"]
                              for name in MAINS}
    cases = []
    xml = folder/"xml/TEST-junit-jupiter.xml"
    if corrected:
        suite = ET.parse(xml).getroot()
        assert suite.get("tests") == "6" and all(suite.get(k) == "0" for k in ("failures","errors","skipped"))
        original, = (v["publicFile"] for v in baseline["actualPublicXmlIntegration"]
                     if v["sourceName"] == "TEST-junit-jupiter.xml")
        assert pin(original["path"]) == original
        def selected(root):
            return sorted((c.get("classname"), c.get("name")) for c in root.findall("testcase")
                          if c.get("classname").split(".")[-1] in TESTS)
        cases = selected(suite)
        assert len(cases) == 6 and cases == selected(ET.parse(original["path"]).getroot())
    begin_file(folder/"terminal.json", dict(source=host_source, productCore=core, terminalAtUTC=now(),
        actualExit=0, stages=status, cases=cases, physical=output,
        junitAndCoverage=[pin(p) for p in (xml,folder/"unit.exec",folder/"unfiltered.stdout")] if corrected else [],
        ordinaryTestCount=len(cases), actualExternalActions=0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrected", action="store_true")
    main(parser.parse_args().corrected)
