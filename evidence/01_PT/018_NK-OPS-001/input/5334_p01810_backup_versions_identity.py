"""Run only the independent BackupVersions value fixture against the pinned Batch bytes."""

from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path.cwd()
E = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
D = next((ROOT / "documents/400_PGPT/470_PMO").glob("601*"))
MOD = Path("src/schubert-nk-batch")
PKG = Path("dev/codex/schubert/nk/batch/backup")
MAIN = MOD / "src/main/java" / PKG / "BackupVersions.java"
TEST = MOD / "src/test/java" / PKG / "BackupVersionsIdentityTest.java"
TEST_TYPE = "dev.codex.schubert.nk.batch.backup.BackupVersionsIdentityTest"
IDS = dict(zip(("PT-P01810-CATALOG-044A", "PT-P01810-CATALOG-044B"),
               ("everyIndividualClaimParticipatesInValueIdentity",
                "unrelatedIdentityDoesNotAppearInFixedDiagnostic"), strict=True))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def ref(path):
    path = Path(path)
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main(group, retry=False):
    assert group in ("724", "727")
    assert not retry or group == "727"
    start = read(next(D.glob(group + "_*.json")))
    v = start["values"]
    test_ids = dict(zip(v["testIds"], v.get("testMethods", IDS.values()), strict=True))
    count = len(test_ids)
    initial = E / v["run"]
    if retry:
        assert read(initial / "manifest.json")["stageResults"]["pmd"]["actualExit"] == 4
    out = E / "PG40276-p01810-backup-versions-complete-value-retest-v1" if retry else initial
    out.mkdir()
    core = v["productionCoreMain"]
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    delta = subprocess.check_output(["git", "diff", "--name-only", v["source"], source, "--", "src"], text=True)
    assert delta.splitlines() == [str(TEST)]
    assert subprocess.check_output(["git", "show", f"{core}:{MAIN}"]) == MAIN.read_bytes()
    assert subprocess.check_output(["git", "show", f"{source}:{TEST}"]) == TEST.read_bytes()
    assert all(ref(pin["path"]) == pin for pin in v["oracleReferences"])
    _, catalog, _, jar, build = [read(pin["path"]) for pin in v["oracleReferences"]]
    assert catalog["source"] == jar["sourceCore"] == build["sourceCore"] == core
    assert ref(MAIN)["sha256"] == build["sourceInputs"][str(MAIN)]
    artifact = jar["jars"]["batch"]["artifact"]
    jar_path = Path(artifact["path"])
    status = jar_path.stat(follow_symlinks=False)
    assert jar_path.resolve() == jar_path and status.st_uid == 1000 and status.st_nlink == 1
    jar_data = jar_path.read_bytes()
    assert sha(jar_data) == artifact["sha256"]
    member = str(PKG / "BackupVersions.class")
    with ZipFile(io.BytesIO(jar_data)) as archive:
        assert archive.namelist().count(member) == 1
        class_data = archive.read(member)
    assert sha(class_data) == build["physicalClassHashes"]["batch"][member]
    previous = read(next(D.glob("584_*.json")))["values"]["oracleReferences"]
    static, toolchain = [read(item["path"]) for item in previous[2:4]]
    assert all(ref(item["path"]) == item for item in previous[2:4])
    java, javac = [Path(toolchain[key]["path"]) for key in ("jdk", "javaC")]
    assert ref(java) == toolchain["jdk"] and ref(javac) == toolchain["javaC"]
    jars = dict((label, toolchain["tools"][file]) for label, file in (
        ("junit", "junit-platform-console-standalone-1.13.4.jar"),
        ("agent", "org.jacoco.agent-0.8.15-runtime.jar"),
        ("annotation", "jspecify-1.0.1.jar"),
    ))
    assert all(ref(item["path"]) == item for item in jars.values())
    fixture = ref(TEST)
    physical = dict(name=member, sha256=sha(class_data))
    stages = {}
    began = datetime.now(timezone.utc).isoformat()

    def execute(name, argv):
        result = subprocess.run([str(part) for part in argv], capture_output=True, timeout=35)
        path = out / (name + ".log.gz")
        path.write_bytes(gzip.compress(result.stdout + result.stderr, mtime=0))
        stages[name] = dict(actualExit=result.returncode, argv=[str(part) for part in argv], log=ref(path))
        return result

    def terminal(exit_code, extra=None):
        report = dict(actualExit=exit_code, source=source, sourceCore=core, startEvent=start["eventId"], classData=physical,
                      jar=artifact, fixture=fixture, testIds=test_ids, stageResults=stages,
                      caseCount=0, testResultsNotStarted="unit" not in stages, newFormalAcceptance=0,
                      actualBackupDbNativeOperations=0, priorTestsReplayed=0, verifier=ref(__file__),
                      startedAtUTC=began, terminalAtUTC=datetime.now(timezone.utc).isoformat())
        report.update(extra or {})
        write(out / "manifest.json", report)
        return exit_code

    with TemporaryDirectory(prefix="pg40272-versions-") as temp:
        tmp = Path(temp)
        prod = tmp / "product" / member
        prod.parent.mkdir(parents=True)
        prod.write_bytes(class_data)
        classes = tmp / "test"
        classes.mkdir()
        cp = ":".join([str(tmp / "product"), jars["junit"]["path"], jars["annotation"]["path"]])
        build_test = execute("javac", [javac, "--release", "25", "-proc:none", "-Xlint:all", "-Werror",
                                      "-cp", cp, "-d", classes, TEST])
        if build_test.returncode:
            return terminal(build_test.returncode)
        sources = tmp / "sources.txt"
        sources.write_text(str(TEST.resolve()) + "\n")
        pmd = list(static["command"])
        for option, arg in (
            ("--file-list", str(sources)),
            ("--report-file", str(out / "pmd.xml")),
            ("--aux-classpath", f"{java.parent.parent}/lib/jrt-fs.jar:{cp}"),
        ):
            pmd[pmd.index(option) + 1] = arg
        static_dir = java.parents[2] / "static-gates-20261015"
        format_jar = java.parents[2] / "google-java-format-1.36.1-all-deps.jar"
        for name, command in (("format", [java, "-jar", format_jar, "--skip-reflowing-long-strings",
                                          "--dry-run", "--set-exit-if-changed", TEST]),
                              ("checkstyle", [java, "-jar", static_dir / "checkstyle-14.3.0-all.jar", "-c",
                                              ROOT / "tools/quality/static/checkstyle.xml", "-f", "xml",
                                              "-o", out / "checkstyle.xml", TEST]),
                              ("pmd", pmd)):
            result = execute(name, command)
            if result.returncode:
                return terminal(result.returncode)
        xml = out / "xml"
        xml.mkdir()
        binary = out / "jacoco.exec"
        session = out.name.split("-", 1)[0] + "-VERSION-CLAIM-VALUES"
        agent_opt = (f'-javaagent:{jars["agent"]["path"]}=destfile={binary},sessionid={session},'
                     'append=false,includes=dev.codex.schubert.nk.batch.backup.BackupVersions')
        unit = execute("unit", [java, "-Djava.io.tmpdir=" + str(tmp), agent_opt, "-jar", jars["junit"]["path"],
                                "execute", "--disable-banner", "--disable-ansi-colors", "--fail-if-no-tests",
                                "--details=summary", "--class-path",
                                f'{classes}:{tmp / "product"}:{jars["annotation"]["path"]}',
                                "--select-class", TEST_TYPE, "--reports-dir", xml])
        if unit.returncode:
            return terminal(unit.returncode)
        case_xml = xml / "TEST-junit-jupiter.xml"
        tree = ElementTree.parse(case_xml).getroot()
        assert len(tree.findall("testcase")) == count
        assert {item.get("name") for item in tree.findall("testcase")} == {n + "()" for n in test_ids.values()}
        assert [tree.get(k) for k in ("tests", "failures", "errors", "skipped")] == [str(count), "0", "0", "0"]
        decoder = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
        observed = decoder(binary.read_bytes(), {member.removesuffix(".class")})
        assert observed["totalClassRecords"] == 1 and len(observed["sessions"]) == 1
        assert observed["sessions"][0]["labelBytesHex"] == session.encode().hex()
        measure = read(next(E.glob("PG39868-*/manifest.json")))["rawCommand"][:5]
        raw = execute("raw", [*measure, binary, prod])
        assert raw.returncode == 0 and not raw.stderr
        [row] = [line.split("\t") for line in raw.stdout.decode().splitlines() if line.startswith("CLASS\t")]
        assert row[1:4] == [member.removesuffix(".class"),
                           observed["classes"][member.removesuffix(".class")]["crc64"].zfill(16), "true"]
        metrics = {}
        for entry in row[6:]:
            label, missed, covered = entry.split(":")
            metrics[label] = dict(missed=int(missed), covered=int(covered))
        expected = v.get("terminalExpectedCounters")
        covered = expected is None or all(metrics[name] == dict(missed=0, covered=value)
                                          for name, value in expected.items())
        return terminal(0 if covered else 1, dict(caseCount=count, testResultsNotStarted=False, expectedCaseCount=count,
                                failed=0, errors=0, skipped=0, notRun=0, junitXml=ref(case_xml),
                                exec=ref(binary), crc=row[2], rawCounters=metrics,
                                requiredFourCounterResult=covered if expected is not None else None,
                                necessarySameSourceRetests=count - 2, oneProductClassOnly=True, whole451Accepted=False))


if __name__ == "__main__":
    if sys.argv[1:] == ["727", "--retry"]:
        raise SystemExit(main("727", retry=True))
    raise SystemExit(main(sys.argv[1] if len(sys.argv) == 2 else "724"))
