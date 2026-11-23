"""Run the local Java-only correlation registry and pending reply fixtures."""

import argparse
import os
from pathlib import Path
import runpy
import subprocess
import xml.etree.ElementTree as ET


SUPPORT = runpy.run_path(str(Path(__file__).with_name("5780_p002_portable_reply_envelope.py")))
ROOT, RUNS, OPS, RECORDS, JAVA = (SUPPORT[n] for n in ("ROOT", "RUNS", "OPS", "RECORDS", "JAVA"))
get, pin, git, now, begin_file = (SUPPORT[n] for n in ("get", "pin", "git", "now", "begin_file"))
WEB = Path("src/schubert-nk-web/src")
PACKAGE = "dev/codex/schubert/nk/web/messaging"
PRODUCT = ("PendingReply", "ReplyCorrelationRegistry")
FIXTURES = ("ReplyCorrelationRegistryTest", "ReplyCorrelationTerminalRaceTest")


def main(corrected):
    checkpoint, = RECORDS.glob("3431_*")
    start = get(checkpoint)["values"]
    core = start["productionCoreMain"]
    source = git("rev-parse", "HEAD").decode().strip()
    mains = [WEB/f"main/java/{PACKAGE}/{name}.java" for name in PRODUCT]
    tests = [WEB/f"test/java/{PACKAGE}/{name}.java" for name in FIXTURES]
    for path in mains + tests:
        body = path.read_bytes()
        assert body == git("show", f"{source}:{path}")
        if path in mains:
            assert body == git("show", f"{core}:{path}")
        if not corrected:
            assert body == git("show", f'{start["source"]}:{path}')
    if corrected:
        assert all(f.read_bytes() != git("show", f'{start["source"]}:{f}') for f in tests)
    support, = OPS.glob("PG43118*/manifest.json")
    deps = get(support)["classpath"]
    tooling = [x for x in deps if Path(x["path"]).name.startswith(
        ("jspecify-", "junit-platform-console-standalone-"))]
    assert len(tooling) == 2 and all(pin(x["path"]) == x for x in tooling)
    run = "PG43158-p00502-registry-fixture-finite-v1" if corrected else start["run"]
    output = RUNS/run
    output.mkdir(mode=0o700)
    target = output/"target/classes"
    test_dir = output/"test"
    for directory in (target, test_dir, output/"xml", output/"meter"):
        directory.mkdir(parents=True)
    prior = RUNS/"PG43130-f03-reply-factory-enum-current-v2"
    baseline = get(prior/"begin.json")["stages"]
    sdk = os.pathsep.join(x["path"] for x in tooling)
    cp = os.pathsep.join((str(target), sdk))
    javac = [
        str(JAVA/"javac"), "--release", "25", "-g", "-Xlint:all", "-Werror",
        "-proc:none", "-implicit:none",
    ]
    stages = {
        "format": [*baseline["format"][:-2], *map(str, tests)],
        "main": [*javac, "-cp", sdk, "-d", str(target), *map(str, mains)],
        "fixture": [*javac, "-cp", cp, "-d", str(test_dir), *map(str, tests)],
    }
    if corrected:
        jacoco = next(x.split("=", 1)[0] for x in baseline["junit"] if x.startswith("-javaagent:"))
        stages["junit"] = [
            str(JAVA/"java"), "-Dfile.encoding=UTF-8", "-Duser.timezone=Asia/Tokyo",
            "-Djunit.jupiter.extensions.autodetection.enabled=false",
            "-Djunit.jupiter.execution.parallel.enabled=false", "-Djunit.jupiter.execution.timeout.default=30 s",
            f"{jacoco}=destfile={output/'unit.exec'},append=false,sessionid={run}",
            "-cp", os.pathsep.join((str(test_dir), cp)),
            "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-ansi-colors",
            "--fail-if-no-tests", "--reports-dir", str(output/"xml"),
        ]
        for name in FIXTURES:
            stages["junit"].extend(("--select-class", f"{PACKAGE.replace('/', '.')}.{name}"))
    for key in ("rawCompile", "unfiltered", "style", "pmd", "spotbugs"):
        if not corrected and key in ("rawCompile", "unfiltered"):
            continue
        cmd = [arg.replace(str(prior), str(output)) for arg in baseline[key]]
        if key == "style":
            cmd = [*cmd[:-2], *map(str, tests)]
        if key == "unfiltered":
            cmd = [*cmd[:-1], *(str(target/PACKAGE/(name+".class")) for name in PRODUCT)]
        if key in ("pmd", "spotbugs"):
            flag = "--aux-classpath" if key == "pmd" else "-auxclasspath"
            cmd[cmd.index(flag)+1] = cp
        stages[key] = cmd
    (output/"current-static-sources.txt").write_text("".join(f"{f}\n" for f in tests))
    begin_file(output/"begin.json", dict(source=source, productCore=core, startUTC=now(),
        inputs=list(map(pin,mains)), fixtures=list(map(pin,tests)), stages=stages, sdk=tooling))
    statuses = {}
    for key, cmd in stages.items():
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=110, check=False)
        (output/f"{key}.stdout").write_bytes(result.stdout)
        (output/f"{key}.stderr").write_bytes(result.stderr)
        statuses[key] = result.returncode
        print(key, result.returncode, flush=True)
        assert result.returncode in {"pmd":{0,4}, "spotbugs":{0,1}}.get(key,{0}), key
    archive = sorted(target.rglob("*.class"))
    assert {p.stem for p in archive} == set(PRODUCT)
    evidence = dict(source=source, productCore=core, actualExit=0, terminalAtUTC=now(),
        stages=statuses, physical=[dict(className=p.stem, sha256=pin(p)["sha256"]) for p in archive])
    if corrected:
        receipt = output/"xml/TEST-junit-jupiter.xml"
        suite = ET.parse(receipt).getroot()
        assert suite.get("tests") == "11" and all(suite.get(k) == "0" for k in ("failures","errors","skipped"))
        evidence["cases"] = sorted((c.get("classname"), c.get("name")) for c in suite.findall("testcase"))
        evidence["dynamic"] = list(map(pin, [receipt, output/"unit.exec", output/"unfiltered.stdout"]))
    else:
        evidence["cases"] = []
    begin_file(output/"terminal.json", evidence)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrected", action="store_true")
    main(parser.parse_args().corrected)
