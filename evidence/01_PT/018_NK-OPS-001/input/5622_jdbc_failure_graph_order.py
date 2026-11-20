"""Verify the SSC-461 JDBC exception order from original JDK Throwable objects."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


h = runpy.run_path(str(Path(__file__).with_name("5609_scr012_count_underclaim.py")))
BIN, OPS, check, pin, read, successful_case = (
    h[key] for key in ("BIN", "OPS", "check", "pin", "read", "successful_case")
)
RUN = "PG41210-f02-ssc461-jdbc-order-identity-v1"
FIXED = "PG41214-f02-ssc461-jdbc-order-identity-fixed-v1"
OWNER = "dev/codex/schubert/nk/api/bootstrap/"
STORAGE = "dev/codex/schubert/nk/storage/StorageIoException"
BOOTSTRAP = Path("src/schubert-nk-bootstrap/src")
TARGET = [OWNER + "JdbcFailureGraph", STORAGE, STORAGE + "$Reason"]
TEST = BOOTSTRAP/"test/java"/(OWNER+"JdbcFailureGraphOrderTest.java")
TEST_BINARY = OWNER+"JdbcFailureGraphOrderTest"
MAINS = [BOOTSTRAP/"main/java"/(TARGET[0]+".java"),
         Path("src/schubert-nk-storage/src/main/java")/(STORAGE+".java")]
TEST_NAMES = {
    "queueRanksCauseAndSuppressedEntriesBeforeSqlNextAtTheSameDepth()": "PT-OPS-JDBCGRAPH006",
    "closerSuppressedErrorWinsOverAnEarlierButDeeperCause()": "PT-OPS-JDBCGRAPH007",
    "sameSqlObjectsAreQueriedOnceWhenNextAndCauseLinkBack()": "PT-OPS-JDBCGRAPH008",
}


def main(mode):
    recover = mode == "--recover"
    run = FIXED if mode == "--fixed" else RUN
    group, = Path("documents/400_PGPT/470_PMO").glob("601_*/1640_*.json")
    scope = read(group)["values"]
    for ref in scope["oracleReferences"]:
        assert pin(Path(ref["path"])) == ref
    _, design, old_graph, _ = [Path(ref["path"]) for ref in scope["oracleReferences"]]
    previous = read(old_graph)
    assert previous["actualExit"] == 0 and previous["ordinaryTests"] == 5
    canonical = subprocess.check_output(["git", "show", f'{scope["canonicalDesignSource"]}:{design}'],
                                       timeout=15).decode()
    assert "SSC-461 SQL例外graph" in canonical and "幅優先キュー" in canonical
    for src in MAINS:
        for rev in (scope["productionCoreMain"], previous["productionCoreMain"]):
            assert subprocess.check_output(["git", "show", f"{rev}:{src}"], timeout=12) == src.read_bytes()
    fixture_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, timeout=12).strip()
    if mode == "--fixed":
        assert subprocess.check_output(["git", "show", f"{fixture_head}:{TEST}"], timeout=12) == TEST.read_bytes()
        initial = read(OPS/RUN/"manifest.json")
        assert initial["inputSources"][-1]["sha256"] != pin(TEST)["sha256"]
    sdk, = OPS.glob("PG37996-*/manifest.json")
    deps = [Path(p) for p in read(sdk)["dependencies"] if Path(p).name in {
        "jspecify-1.0.1.jar", "junit-platform-console-standalone-1.13.4.jar"
    }]
    assert len(deps) == 2 and all(pin(p)["sha256"] == read(sdk)["dependencies"][str(p)] for p in deps)
    old_unit, = OPS.glob("PG37552-*/unit-manifest.json")
    known = read(old_unit)
    agent_arg, = [arg for arg in known["command"] if arg.startswith("-javaagent:")]
    agent = Path(agent_arg.removeprefix("-javaagent:").split("=", 1)[0])
    assert pin(agent)["sha256"] == known["measurementAgentSha256"]
    cfg = Path("tools/quality/static/checkstyle.xml")
    fmt = Path("../toolchain/google-java-format-1.36.1-all-deps.jar")
    style = Path("../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar")
    stages = {}
    stages["format"], checked = check([BIN/"java", "-jar", fmt, "--dry-run", "--set-exit-if-changed", TEST])
    assert checked.returncode == 0, checked.stderr
    stages["checkstyle"], checked = check([BIN/"java", "-jar", style, "-c", cfg, "-f", "xml", TEST])
    assert checked.returncode == 0 and not ET.fromstring(checked.stdout).findall(".//error")
    local = (Path("../pgpt-runs/PG379") / run).resolve()
    assert local.exists() == recover
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-jdbc-graph-order-") as temp:
        classes = Path(temp) / "classes"
        classes.mkdir()
        cp = os.pathsep.join(map(str, [classes, *deps]))
        stages["compile"], built = check([BIN/"javac", "-g", "--release", "25", "-Xlint:all",
            "-Werror", "-proc:none", "-cp", cp, "-d", classes, *MAINS, TEST])
        assert built.returncode == 0, built.stderr
        paths = [classes/(name + ".class") for name in TARGET]
        published_physical = local/"sealed"
        xml = local/"xml"
        unit = local/"unit.exec"
        terminal = local/"terminal.json"
        if recover:
            assert all(path.read_bytes() == (published_physical/path.name).read_bytes() for path in paths)
            stages["junit"] = read(terminal)
            assert stages["junit"]["command"][-1] == TEST_BINARY.replace("/", ".")
            assert any(str(unit) in part and run in part for part in stages["junit"]["command"])
        else:
            local.mkdir()
            published_physical.mkdir()
            for path in paths:
                (published_physical/path.name).write_bytes(path.read_bytes())
            stages["junit"], _ = check([BIN/"java", "-Dfile.encoding=UTF-8",
                f"-javaagent:{agent}=destfile={unit},append=false,sessionid={run}", "-cp", cp,
                "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-banner",
                "--details=summary", "--fail-if-no-tests", "--reports-dir", xml,
                "--select-class", TEST_BINARY.replace("/", ".")])
            terminal.write_text(json.dumps(stages["junit"], indent=2) + "\n")
        archived = xml/"TEST-junit-jupiter.xml"
        root = ET.parse(archived).getroot()
        cases = root.findall("testcase")
        assert set(case.get("name") for case in cases) == set(TEST_NAMES)
        assert all(successful_case(case) for case in cases) and stages["junit"]["exit"] == 0
        assert tuple(root.get(k) for k in ("tests", "failures", "errors", "skipped")) == ("3", "0", "0", "0")
        original = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"](
            unit.read_bytes(), {*TARGET[:2], TEST_BINARY, TEST_BINARY+"$CountingSql"}
        )["classes"]
        crc = runpy.run_path(str(Path(__file__).with_name("5593_p01808_original_name_binding.py")))["class_id"]
        for name, row in original.items():
            assert int(row["crc64"], 16) == crc((classes/(name+'.class')).read_bytes())
        assert not any(case.get("classname") != TEST_BINARY.replace("/", ".") for case in cases)
    out = OPS/run
    out.mkdir()
    for name, archive in (("unit.exec", unit), ("jupiter.xml", archived)):
        (out/name).write_bytes(archive.read_bytes())
    receipt = dict(run=run, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                   source=scope["productionCoreMain"], group=pin(group), actualExit=stages["junit"]["exit"],
                   tests=3, failures=0, errors=0, skipped=0, notRun=0, oldTestsReplayed=0,
                   testIds=TEST_NAMES, inputSources=list(map(pin, [*MAINS, TEST])),
                   actualResourcesUsed=[], priorEvidence=pin(old_graph), dependencies=list(map(pin, deps)),
                   stages=stages, originalArtifacts=list(map(pin, [terminal, unit, archived])),
                   originalProbeRecords=original, sealedPhysical=list(map(pin, sorted(published_physical.iterdir()))),
                   naturallyUnloaded=[TARGET[2]], recoveredOriginalWithoutTestRerun=recover,
                   fixedFixtureCommit=fixture_head if mode == "--fixed" else None,
                   wholeF02=False, whole451=False, formalDelta=0)
    target = out/"manifest.json"
    with target.open("x") as file:
        json.dump(receipt, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(target), len(cases), {name: len(row["hitProbeIds"]) for name, row in original.items()})


if __name__ == "__main__":
    assert sys.argv[1:] in ([], ["--recover"], ["--fixed"])
    main((sys.argv[1:] or ["--baseline"])[0])
