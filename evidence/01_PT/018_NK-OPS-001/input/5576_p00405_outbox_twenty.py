"""Join all allowed borrowed-Outbox tests on a single session of the exact current class files."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
SDK = Path.cwd().parent / "toolchain"
JAVA = SDK / "jdk-25.0.4/bin/java"
DOMAIN = "dev.codex.schubert.nk.api.monitoring."
NAMESPACE = DOMAIN.replace(".", "/")
COLLECTOR = "OutboxMetricCollector"
REPO = "OutboxObservationRepository"
NEW_METHOD = "outboxDb012CompleteReadWithTwoCloseFailuresKeepsFirstReleaseAsPrimary"
RAW_SOURCE = "e02e75b21d82f903b886ba8951e04da15c643489"


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return sha256(data).hexdigest()


def pin(p):
    return dict(path=str(p), sha256=sha(p.read_bytes()))


def git(*parts):
    return subprocess.check_output(["git", *parts], timeout=35)


def ref(prefix, name="manifest.json"):
    p, = OPS.glob(f"{prefix}-*/{name}")
    return p


def read(p):
    return json.loads(p.read_bytes())


def target_class(name):
    if not name.startswith(NAMESPACE):
        return False
    return Path(name).stem.split("$", 1)[0] in {
        COLLECTOR, REPO, "OutboxAgeMetricRecorder", "OutboxRowsMetricRecorder", "package-info",
    }


def main():
    start_path, = Path("documents/400_PGPT/470_PMO").glob("601_*/1525_*")
    start = read(start_path)
    scope = start["values"]
    archive = [Path(r["path"]) for r in scope["oracleReferences"]]
    assert [pin(p) for p in archive] == scope["oracleReferences"]
    focus, historical, original, typed = map(read, archive[1:])
    assert all(x["actualExit"] == 0 for x in [focus, historical, original, typed])
    assert original["tests"] == historical["tests"] == 19
    assert focus["testCounts"] == dict(tests=1, failures=0, errors=0, skipped=0)
    core, run_id = scope["productionCoreMain"], scope["run"]
    expected = {(c["classname"], c["name"].removesuffix("()")) for c in original["cases"]}
    expected.add((DOMAIN + REPO + "Test", NEW_METHOD))
    assert len(expected) == 20
    p = Path("src/schubert-nk-api/src")
    test = [p / "test/java" / NAMESPACE / (owner+"Test.java") for owner in (COLLECTOR, REPO)]
    prod = [Path(row["path"]) for row in focus["sourcePins"]]
    prod.append(p / "main/java" / NAMESPACE / (COLLECTOR + ".java"))
    assert len(prod) == 5
    for path in prod + test:
        assert path.read_bytes() == git("show", f"{core}:{path}")
    for path in prod:
        basis = historical["productionCoreMain"] if path.stem == COLLECTOR else typed["source"]
        assert git("show", f"{basis}:{path}") == path.read_bytes()
    for path in test:
        if path.name == REPO + "Test.java":
            assert pin(path) == focus["fixture"]
        else:
            assert git("show", f"{original['begin']['source']}:{path}") == path.read_bytes()
    retained = {row["classPath"]: row["sha256"] for row in typed["generatedPhysical"]
                if target_class(row["classPath"])}
    typed_old = read(Path(historical["proofs"]["prepare"]["path"]))
    collector_key = NAMESPACE + COLLECTOR + ".class"
    retained[collector_key] = typed_old["physicalClassHashes"][collector_key]
    assert len(retained) == 9
    deps = focus["dependencyPins"]
    assert all(pin(Path(i["path"])) == i for i in deps)
    libs = os.pathsep.join(i["path"] for i in deps)
    junit = [i["path"] for i in deps if "junit-platform-console-standalone" in i["path"]]
    assert len(junit) == 1
    agent = SDK / "m2/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    raw_inputs = read(ref("PG31432", "compile.json"))["dependencies"]
    assert all(pin(Path(i["path"])) == i for i in raw_inputs)
    aux = os.pathsep.join(i["path"] for i in raw_inputs)
    output = OPS / run_id
    output.mkdir()
    private = Path.cwd().parent / "pgpt-runs/PG379" / run_id
    private.mkdir(mode=0o700)
    stages = {}

    def call(label, *args):
        cmd = list(map(str, args))
        result = subprocess.run(cmd, capture_output=True, timeout=65,
                                env={"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"})
        (private/(label+".stdout")).write_bytes(result.stdout)
        (private/(label+".stderr")).write_bytes(result.stderr)
        stages[label] = dict(command=cmd, actualExit=result.returncode, terminalAtUTC=utc(),
                             stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr))
        if result.returncode:
            raise SystemExit(result.returncode)
        return result.stdout

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-outbox-current-") as d:
        tmp = Path(d)
        production, fixtures, raw_classes = (tmp / name for name in ("prod", "test", "raw"))
        javac = JAVA.with_name("javac")
        strict = (javac, "--release", 25, "-g", "-proc:none", "-Xlint:all", "-Werror",
                  "-implicit:none", "-sourcepath", "")
        call("main", *strict, "-cp", libs, "-d", production, *prod)
        physical = {p.relative_to(production).as_posix(): sha(p.read_bytes()) for p in production.rglob("*.class")}
        assert physical == retained, {name for name, val in physical.items() if retained.get(name) != val}
        call("test-compile", *strict, "-cp", f"{production}:{libs}", "-d", fixtures, *test)
        session = "PG41076"
        data = private / "unit.exec"
        xml = private / "junit"
        init = private / "class-init.log"
        call("unit", JAVA, f"-javaagent:{agent}=destfile={data},append=false,sessionid={session}",
             f"-Xlog:class+init=info:file={init}", "-jar", junit[0], "execute", "--disable-ansi-colors",
             "--disable-banner", "--class-path", f"{production}:{fixtures}:{libs}", "--reports-dir", xml,
             "--select-class", DOMAIN + COLLECTOR + "Test", "--select-class", DOMAIN + REPO + "Test",
             "--fail-if-no-tests")
        xml = xml / "TEST-junit-jupiter.xml"
        root = ET.parse(xml).getroot()
        entries = root.findall("testcase")
        assert len(entries) == 20 and {(r.attrib["classname"], r.attrib["name"].removesuffix("()"))
                                       for r in entries} == expected
        assert all(not any(el.tag in ("failure", "error", "skipped") for el in row) for row in entries)
        forbidden = ("org/postgresql/", "TemporaryInfrastructureException", "FingerprintKeyRing",
                     "ResponseSnapshotCodec", "WebStartupException", "ApiOutboxObservationPump")
        assert all(item not in init.read_text() for item in forbidden)
        raw_tool = tmp / "UnfilteredCodeMeasurement.java"
        raw_tool.write_bytes(git("show", f"{RAW_SOURCE}:tools/quality/jacoco/{raw_tool.name}"))
        call("raw-compile", javac, "--release", 25, "-Xlint:all", "-Werror", "-cp", aux,
             "-d", raw_classes, raw_tool)
        raw = call("raw", JAVA, "-cp", f"{raw_classes}:{aux}",
                   "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                   data, *[production/name for name in sorted(physical)])
        table = output / "raw.tsv"
        table.write_bytes(raw)
        rows = []
        for line in raw.decode().splitlines():
            cells = line.split("\t")
            if cells[0] == "CLASS":
                name = cells[1]
                assert name+".class" in physical
                counters = {key: {"missed": int(missed), "covered": int(hit)}
                            for key, missed, hit in (item.split(":") for item in cells[6:])}
                rows.append(dict(className=name, crc64=cells[2], matched=cells[3]=="true",
                                 counters=counters, classSha256=physical[name+".class"]))
        assert len(rows) == 9
        targets = [row for row in rows if Path(row["className"]).name in
                   {COLLECTOR, REPO, REPO+"$Snapshot"}]
        assert len(targets) == 3 and all(row["matched"] for row in targets)
        assert all(c["missed"] == 0 for row in targets for c in row["counters"].values())
        aggregate = {key: sum(row["counters"][key]["covered"] for row in targets)
                     for key in targets[0]["counters"]}
        assert aggregate == {key: item["covered"] for key, item in historical["rawTargets"].items()}
    safe = ET.Element("testsuite", name="OutboxBorrowedScopes", tests="20", failures="0", errors="0", skipped="0")
    for cls, method in sorted(expected):
        ET.SubElement(safe, "testcase", classname=cls, name=method)
    safe_xml = output / "testcases.safe.xml"
    ET.ElementTree(safe).write(safe_xml, encoding="utf-8", xml_declaration=True)
    m = output / "manifest.json"
    with m.open("x") as f:
        json.dump(dict(actualExit=0, productionCore=core, source=git("rev-parse","HEAD").decode().strip(),
                       run=run_id, tests=20, suites=2, errors=0, failures=0, skipped=0, notRun=0,
                       buildSourcePins=[pin(x) for x in prod], testPins=[pin(x) for x in test],
                       tools=deps+[pin(agent)], firstAttemptDynamicSuccess=True, unitRuns=1,
                       currentCollectorTypedClassExact=True, other8CurrentTypedClassesExact=True,
                       unitXmlPrivate=pin(xml), unitXmlPublic=pin(safe_xml), classInitPrivate=pin(init),
                       execRun=pin(data), session=session, measured=rows, rawTargets=aggregate, rawTable=pin(table),
                       previous19=pin(archive[2]), previousOne=pin(archive[1]), originalExecMerged=False,
                       backendOperations=0, postgresDriverOrHeldTypeInit=0, stages=stages,
                       productFormalDelta=0, whole451=False, terminalAtUTC=utc()), f,
                  indent=2,ensure_ascii=False)
        f.write("\n")
    print(pin(m), aggregate)


if __name__ == "__main__":
    main()
