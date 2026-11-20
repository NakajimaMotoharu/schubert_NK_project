"""Direct SS333 parser PT with separate failing baseline and changed-source receipts."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


helpers = runpy.run_path(str(Path(__file__).with_name("5609_scr012_count_underclaim.py")))
BIN, OPS, WEB = (helpers[key] for key in ("BIN", "OPS", "WEB"))
check, pin, read, successful_case = (
    helpers[key] for key in ("check", "pin", "read", "successful_case")
)
PACKAGE = "dev.codex.schubert.nk.web.media"
DIR = Path(PACKAGE.replace(".", "/"))
MAIN_NAME = "HttpByteRangeParser"
MAIN = WEB / "main/java" / DIR / (MAIN_NAME + ".java")
NEW = "HttpByteRangeUnitTokenTest"
OLD = ("HttpByteRangeParserTest", "HttpByteRangeNamespaceContractTest",
       "HttpByteRangeLongBoundaryTest")
NEW_CASES = {
    "rejectsNonAsciiCaseEquivalentInTheUnit()": "PT-MED-RANGE-UNIT-001",
    "acceptsMixedAsciiCaseAndSelectsTheFirstInterval()": "PT-MED-RANGE-UNIT-002",
}


def main(mode):
    assert mode in {"red", "green"}
    baseline = mode == "red"
    run = "PG41202-range-unit-ascii-baseline-v1" if baseline else "PG41204-range-unit-ascii-affected-v1"
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1634_*.json")
    context = read(start)["values"]
    assert all(pin(Path(row["path"])) == row for row in context["oracleReferences"])
    design = Path(context["oracleReferences"][1]["path"])
    canon = subprocess.check_output(
        ["git", "show", f'{context["canonicalDesignSource"]}:{design}'], timeout=15
    )
    assert "case-insensitive" in canon.decode() and "bytes=" in canon.decode()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, timeout=10).strip()
    core = context["productionCoreMain"] if baseline else head
    names = (NEW,) if baseline else (NEW, *OLD)
    tests = [WEB / "test/java" / DIR / (name + ".java") for name in names]
    assert subprocess.check_output(["git", "show", f"{core}:{MAIN}"], timeout=15) == MAIN.read_bytes()
    if not baseline:
        for test in tests:
            assert subprocess.check_output(["git", "show", f"{head}:{test}"], timeout=15) == test.read_bytes()
    old_unit, = OPS.glob("PG37552-*/unit-manifest.json")
    old = read(old_unit)
    option, = [part for part in old["command"] if part.startswith("-javaagent:")]
    agent = Path(option.removeprefix("-javaagent:").split("=", 1)[0])
    assert pin(agent)["sha256"] == old["measurementAgentSha256"]
    console = Path("../toolchain/junit-platform-console-standalone-1.13.4.jar").resolve()
    sdk, = OPS.glob("PG37996-*/manifest.json")
    assert pin(console)["sha256"] == read(sdk)["dependencies"][str(console)]
    formatter = Path("../toolchain/google-java-format-1.36.1-all-deps.jar")
    style = Path("../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar")
    changed = [tests[0]] if baseline else [MAIN, tests[0]]
    results = {}
    results["format"], fmt = check([BIN/"java", "-jar", formatter, "--dry-run",
                                     "--set-exit-if-changed", *changed])
    results["checkstyle"], cs = check([BIN/"java", "-jar", style, "-c",
                                        "tools/quality/static/checkstyle.xml", "-f", "xml", *changed])
    assert fmt.returncode == cs.returncode == 0, (fmt.stderr, cs.stdout)
    assert not ET.fromstring(cs.stdout).findall(".//error")
    local = (Path("../pgpt-runs/PG379") / run).resolve()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-range-unit-") as scratch:
        classes = Path(scratch) / "classes"
        classes.mkdir()
        results["compile"], built = check([BIN/"javac", "-g", "--release", "25", "-Xlint:all",
                                            "-Werror", "-proc:none", "-cp", console, "-d",
                                            classes, MAIN, *tests])
        assert built.returncode == 0, built.stderr
        physical = sorted((classes / DIR).glob(MAIN_NAME + "*.class"))
        assert len(physical) == 5
        local.mkdir()
        sealed = local / "physical"
        sealed.mkdir()
        for item in physical:
            (sealed / item.name).write_bytes(item.read_bytes())
        track, reports = local / "unit.exec", local / "xml"
        selectors = [argument for name in names for argument in ("--select-class", PACKAGE + "." + name)]
        results["junit"], executed = check([BIN/"java", "-Dfile.encoding=UTF-8",
            f"-javaagent:{agent}=destfile={track},append=false,sessionid={run}",
            "-cp", os.pathsep.join(map(str, (classes, console))),
            "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-banner", "--details=summary",
            "--fail-if-no-tests", "--reports-dir", reports, *selectors])
        terminal = local / "terminal.json"
        terminal.write_text(json.dumps(results["junit"], indent=2) + "\n")
        raw = reports / "TEST-junit-jupiter.xml"
        suite = ET.parse(raw).getroot()
        cases = []
        for item in suite.findall("testcase"):
            good = successful_case(item)
            name = item.get("name")
            testcase = {"name": name, "classname": item.get("classname"),
                        "testId": NEW_CASES.get(name), "result": "PASS" if good else "FAIL"}
            if not good:
                failure = item.find("failure")
                assert baseline and name == "rejectsNonAsciiCaseEquivalentInTheUnit()"
                assert failure is not None and "Partial[start=0, end=0]" in failure.get("message", "")
                testcase["expected"] = "Unsatisfiable"
                testcase["actual"] = "Partial[start=0, end=0]"
            cases.append(testcase)
        expected = (2, 1, 0, 0) if baseline else (8, 0, 0, 0)
        assert tuple(int(suite.get(k)) for k in ("tests", "failures", "errors", "skipped")) == expected
        assert len(cases) == expected[0] and executed.returncode == (1 if baseline else 0)
        assert {c["testId"] for c in cases if c["testId"]} == set(NEW_CASES.values())
    manifest = dict(run=run, source=head, productionCore=core, actualExit=executed.returncode,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat(), group=pin(start),
                    main=pin(MAIN), testsInput=list(map(pin, tests)), tests=expected[0],
                    failures=expected[1], errors=0, skipped=0, notRun=0,
                    cases=cases, stages=results, junit=pin(console), agent=pin(agent),
                    originals=list(map(pin, (terminal, track, raw))),
                    physical=list(map(pin, sorted(sealed.iterdir()))),
                    actualExternalOperations=0, oldExecCombined=False, formalDelta=0)
    pub = OPS / run
    pub.mkdir()
    for name, path in (("unit.exec", track), ("jupiter.xml", raw)):
        (pub / name).write_bytes(path.read_bytes())
    dest = pub / "manifest.json"
    with dest.open("x") as file:
        json.dump(manifest, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(dest), expected, "actualExit", executed.returncode)


if __name__ == "__main__":
    main(sys.argv[1])
