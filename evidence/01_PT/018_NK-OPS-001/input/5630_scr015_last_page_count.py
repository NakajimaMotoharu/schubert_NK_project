"""Run the independent SCR015 final-page cardinality test with a closed Web source set."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


a = runpy.run_path(str(Path(__file__).with_name("5609_scr012_count_underclaim.py")))
BIN, OPS, WEB, check, pin, read, successful_case = (
    a[k] for k in ("BIN", "OPS", "WEB", "check", "pin", "read", "successful_case")
)
ROOT = "dev/codex/schubert/nk/web/"
TYPE = ROOT+"view/UserListLastPageCountTest"
TEST = WEB/"test/java"/(TYPE+".java")
VIEW = ROOT+"view/UserListViewModel"
MAINS = [WEB/"main/java"/(ROOT+name+".java") for name in (
    "view/UserListViewModel", "view/PageViewModel", "view/TopBarViewModel",
    "session/SessionPrincipal", "form/UserSearchForm"
)]
RUN = "PG41226-scr015-last-page-over-supplied-v1"


def main():
    group, = Path("documents/400_PGPT/470_PMO").glob("601_*/1649_*.json")
    plan = read(group)["values"]
    for row in plan["oracleReferences"]:
        assert pin(Path(row["path"])) == row
    evidence = [Path(row["path"]) for row in plan["oracleReferences"]]
    _, design, spec, old_test, form_result = evidence
    assert "UserListViewModel.success" in spec.read_text()
    assert "user006IndependentProjectionCountIdentityAndCOrder" in old_test.read_text()
    canon = subprocess.check_output(["git", "show", f'{plan["canonicalDesignSource"]}:{design}'], timeout=12)
    assert "100/50件page共通" in canon.decode()
    for path in MAINS:
        assert subprocess.check_output(["git", "show", f'{plan["productionCoreMain"]}:{path}'],
                                       timeout=12) == path.read_bytes()
    sdk, = OPS.glob("PG37996-*/manifest.json")
    deps = read(sdk)["dependencies"]
    dependencies = [Path(key) for key in deps if Path(key).name in {
        "current-protocol176.jar", "jspecify-1.0.1.jar",
        "junit-platform-console-standalone-1.13.4.jar", "spring-core-7.0.9.jar", "spring-web-7.0.9.jar"
    }]
    assert len(dependencies) == 5 and all(pin(path)["sha256"] == deps[str(path)] for path in dependencies)
    blocked_names = {"TemporaryInfrastructureException", "FingerprintKeyRing",
                     "ResponseSnapshotCodec", "WebStartupException"}
    for path in dependencies:
        with ZipFile(path) as jar:
            assert all(Path(n).stem.split("$")[0] not in blocked_names for n in jar.namelist())
    tool, = OPS.glob("PG37552-*/unit-manifest.json")
    known = read(tool)
    option, = [part for part in known["command"] if part.startswith("-javaagent:")]
    agent = Path(option.removeprefix("-javaagent:").split("=", 1)[0])
    assert pin(agent)["sha256"] == known["measurementAgentSha256"]
    format_jar = Path("../toolchain/google-java-format-1.36.1-all-deps.jar")
    style = Path("../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar")
    stages = {}
    stages["format"], fmt = check([BIN/"java", "-jar", format_jar, "--dry-run", "--set-exit-if-changed", TEST])
    stages["checkstyle"], cs = check([BIN/"java", "-jar", style, "-c", "tools/quality/static/checkstyle.xml",
                                      "-f", "xml", TEST])
    assert fmt.returncode == cs.returncode == 0 and not ET.fromstring(cs.stdout).findall(".//error")
    local = (Path("../pgpt-runs/PG379")/RUN).resolve()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-scr015-count-") as temp:
        classes = Path(temp)/"classes"
        classes.mkdir()
        cp = os.pathsep.join(map(str, (classes, *dependencies)))
        stages["compile"], compiled = check([BIN/"javac", "--release", "25", "-g", "-Xlint:all",
                                            "-Werror", "-proc:none", "-cp", cp, "-d", classes, *MAINS, TEST])
        assert compiled.returncode == 0, compiled.stderr
        local.mkdir()
        original, xml = local/"unit.exec", local/"xml"
        selected_name = TYPE.replace("/", ".")
        stages["junit"], unit = check([BIN/"java", "-Dfile.encoding=UTF-8",
                                      f"-javaagent:{agent}=destfile={original},append=false,sessionid={RUN}",
                                      "-cp", cp, "org.junit.platform.console.ConsoleLauncher", "execute",
                                      "--disable-banner", "--details=summary", "--fail-if-no-tests",
                                      "--reports-dir", xml, "--select-class", selected_name])
        terminal = local/"terminal.json"
        terminal.write_text(json.dumps(stages["junit"], indent=2) + "\n")
        archived = xml/"TEST-junit-jupiter.xml"
        suite = ET.parse(archived).getroot()
        [case] = suite.findall("testcase")
        assert case.get("classname") == selected_name and successful_case(case) and unit.returncode == 0
        assert tuple(suite.get(key) for key in ("tests", "failures", "errors", "skipped")) == ("1", "0", "0", "0")
        assert case.get("name") == "rejectsAnExtraSortedRowOnTheSingleRowLastPage()"
        target = {VIEW, VIEW+"$Row", TYPE}
        raw = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"](
            original.read_bytes(), target
        )["classes"]
        crc = runpy.run_path(str(Path(__file__).with_name("5593_p01808_original_name_binding.py")))["class_id"]
        for name, row in raw.items():
            path = classes/(name+".class")
            assert int(row["crc64"], 16) == crc(path.read_bytes()) and row["hitProbeIds"]
        compiled_hash = {str(p.relative_to(classes)):pin(p)["sha256"] for p in sorted(classes.rglob("*.class"))}
    pub = OPS/RUN
    pub.mkdir()
    for name, file in (("jupiter.xml", archived), ("unit.exec", original)):
        (pub/name).write_bytes(file.read_bytes())
    outcome = dict(run=RUN, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                   productionCore=plan["productionCoreMain"], actualExit=0,
                   tests=1, failures=0, errors=0, skipped=0, notRun=0,
                   testId="PT-WEB-SCR015-COUNT-001", plan=pin(group), oldCaseSource=pin(old_test),
                   relatedOldFormProof=pin(form_result), testSource=pin(TEST),
                   mainInputs=list(map(pin, MAINS)), dependencies=list(map(pin, dependencies)),
                   compiledPhysical=compiled_hash, originalProbeRecords=raw,
                   independentOffsets=dict(total=51, pageSize=50, requestedPage=2, first=51, last=51, expectedRows=1),
                   stages=stages, originalArtifacts=list(map(pin, (terminal, archived, original))),
                   productRoleProof=False, oldTestsReplayed=0, actualAccountOrDbActions=0,
                   actualHttpActions=0, whole451=False, formalDelta=0)
    result = pub/"manifest.json"
    with result.open("x") as file:
        json.dump(outcome, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(result), len(compiled_hash), list(raw))


if __name__ == "__main__":
    main()
