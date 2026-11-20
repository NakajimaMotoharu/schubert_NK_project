"""Execute the generic Storage graph contract against the admitted packaged classes."""

from datetime import datetime, timezone
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as XML
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5391_f03_storage_current_two_junit.py")))
ROOT, JAVA, JUNIT, AGENT, NULLABILITY, OPS, PLAN, PKG = (H[k] for k in
    ("ROOT", "JAVA", "JUNIT", "AGENT", "NULLABILITY", "OPS", "PLAN", "PKG"))
pin, checked, read, write, run = (H[k] for k in ("pin", "checked", "read", "write", "run"))
PHYSICAL, NAMES, TEST_PATH = (H[k] for k in ("PHYSICAL", "NAMES", "TEST_PATH"))
NEW = {
    "injectedGraphVisitsEachNonFatalObjectOnceInBreadthFirstEdgeOrder()",
    "injectedGraphStopsBeforeFatalOrLaterNodesCanInvokeTheEdge()",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=16)


def main():
    ctx = read(next(PLAN.glob("1694_*.json")))["values"]
    refs = [checked(row) for row in ctx["oracleReferences"]]
    tested = git("rev-parse", "HEAD").decode().strip()
    package, origin = read(refs[3]), read(refs[2])
    assert origin["actualExit"] == 0 and origin["tests"] == 6 and origin["localRawFour100"]
    artifact = checked(package["packagedBuild"]["storage"]["artifact"])
    pkg_name = "src/schubert-nk-storage"
    assert not git("diff", "--name-only", package["source"], tested,
                   "--", pkg_name + "/src/main", pkg_name + "/pom.xml", "src/pom.xml", "pom.xml")
    assert not git("diff", "--name-only", ctx["productionCoreMain"], tested, "--",
                   ":(glob)src/**/src/main/**")
    paths = [TEST_PATH / (name + ".java") for name in NAMES]
    assert set(git("diff", "--name-only", ctx["source"], tested, "--", pkg_name).decode().splitlines()) == {
        paths[0].as_posix()
    }
    out = OPS / ctx["run"]
    out.mkdir()
    private = ROOT.parent / "pgpt-runs/PG379" / ctx["run"]
    private.mkdir(mode=0o700)
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-storage-edge-") as tmp:
        root = Path(tmp)
        src, classes, tests = root / "source", root / "classes", root / "tests"
        src.mkdir()
        inputs = []
        for repo_path in paths:
            scoped = src / repo_path.name
            scoped.write_bytes(git("show", f"{tested}:{repo_path}"))
            inputs.append(scoped)
        with ZipFile(artifact) as jar:
            for name in PHYSICAL:
                obj = classes / name
                obj.parent.mkdir(parents=True, exist_ok=True)
                obj.write_bytes(jar.read(name))
        bodies = {name: pin(classes / name)["sha256"] for name in PHYSICAL}
        strict = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        stages = {"compile": run([*strict, "-cp", f"{classes}:{JUNIT}:{NULLABILITY}", "-d", tests, *inputs],
                                 root, out, "compile")}
        assert stages["compile"]["actualExit"] == 0
        reports = private / "xml"
        original = private / "unit.exec"
        session = "PG41294-F02-STORAGE-EXTRA-EDGE"
        stages["unit"] = run([JAVA, f"-javaagent:{AGENT}=destfile={original},sessionid={session},"
                                   f"append=false,includes={PKG}.StorageIoException*",
                              "-jar", JUNIT, "execute", "--disable-banner", "--disable-ansi-colors",
                              "--fail-if-no-tests", "--class-path", f"{classes}:{tests}",
                              "--reports-dir", reports,
                              *[item for name in NAMES for item in ("--select-class", PKG + "." + name)]],
                             root, out, "unit")
        assert stages["unit"]["actualExit"] == 0
        raw_xml = reports / "TEST-junit-jupiter.xml"
        junit = XML.parse(raw_xml).getroot()
        assert {k: int(junit.attrib[k]) for k in ("tests", "failures", "errors", "skipped")} == {
            "tests": 8, "failures": 0, "errors": 0, "skipped": 0}
        actual = {(item.attrib["classname"], item.attrib["name"]) for item in junit.iter("testcase")}
        expected = {(item["className"], item["name"]) for item in origin["executedExactCases"]}
        assert actual == expected | {(PKG + ".StorageFailureGraphTest", name) for name in NEW}
        cp = H["bin_report"](next(OPS.glob("PG40602-*/manifest.json")))
        stages["coverage"] = run([JAVA, "-cp", cp, "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                                  "--strict-original-exec", original, *[classes / name for name in PHYSICAL]],
                                 root, out, "unfiltered")
        assert stages["coverage"]["actualExit"] == 0
        report = Path(stages["coverage"]["stdout"]["path"]).read_text().splitlines()
        rows = {p[1] + ".class": p[2:] for p in (line.split("\t") for line in report) if p[0] == "CLASS"}
        assert rows.keys() == set(PHYSICAL)
        observed = {name: row[0] for name, row in rows.items()}
        assert observed == origin["classCrc"]
        decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
        raw = decode(original.read_bytes(), {name.removesuffix(".class") for name in PHYSICAL})
        assert [entry["labelBytesHex"] for entry in raw["sessions"]] == [session.encode().hex()]
        assert observed == {n + ".class": d["crc64"] for n, d in raw["classes"].items()}
        coverage = {name: {f.split(":")[0]: list(map(int, f.split(":")[1:])) for f in row[4:]}
                    for name, row in rows.items()}
        assert all(not missed for counters in coverage.values() for missed, _ in counters.values())
        for relative in paths:
            assert git("show", f"{tested}:{relative}") == relative.read_bytes()
    write(out / "manifest.json", dict(
        actualExit=0, run=ctx["run"], source=tested, core=ctx["productionCoreMain"],
        examinedCases=8, newDefinitions=2, earlierCasesRequalified=6, failures=0, errors=0, skipped=0, notRun=0,
        cases=[dict(className=c, method=m) for c, m in sorted(actual)], exactPackagedMain=pin(artifact),
        actualMainClassSha256=bodies, crc=observed, raw=coverage, originalExec=pin(original),
        originalXml=pin(raw_xml), session=session, testInputs=list(map(pin, paths)), prior=pin(refs[2]),
        stages=stages, liveDbOrFileOperations=0, oldExecMerged=False, whole451=False,
        formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(out / "manifest.json"), coverage)


if __name__ == "__main__":
    main()
