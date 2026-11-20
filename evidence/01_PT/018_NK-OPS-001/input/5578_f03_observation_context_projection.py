"""Exercise the immutable observation key in the whole existing monitoring test suite."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
SDK = Path.cwd().parent / "toolchain"
JAVA = SDK / "jdk-25.0.4/bin/java"
M2 = SDK / "m2/repository"
AGENT = SDK / "m2/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
JUNIT = SDK / "junit-platform-console-standalone-1.13.4.jar"
SPECIFY = M2 / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
NAMESPACE = "dev/codex/schubert/nk/batch/monitoring/"
DECODER = "dba164629c:tools/quality/jacoco_readonly_exec_subset.py"
RAW = "e02e75b21d82f903b886ba8951e04da15c643489:tools/quality/jacoco/UnfilteredCodeMeasurement.java"


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return sha256(data).hexdigest()


def pin(p):
    return dict(path=str(p), sha256=sha(p.read_bytes()))


def read(p):
    return json.loads(p.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=25)


def main():
    s, = Path("documents/400_PGPT/470_PMO").glob("601_*/1528_*")
    plan = read(s)["values"]
    refs = [Path(ref["path"]) for ref in plan["oracleReferences"]]
    assert [pin(p) for p in refs] == plan["oracleReferences"]
    old_suite, alert, package = map(read, refs[1:])
    core, run_id = plan["productionCoreMain"], plan["run"]
    assert alert["source"] == package["source"] == core
    sample, = OPS.glob("PG40938-*/manifest.json")
    original = read(sample)
    main_sources = sorted({Path(i["path"]) for i in original["inputs"] if "/src/main/" in i["path"]})
    fixture = Path(original["test"]["path"])
    assert len(main_sources) == 7 and pin(fixture) != original["test"]
    for path in main_sources:
        assert path.read_bytes() == git("show", f"{core}:{path}")
    work_source = git("rev-parse", "HEAD").decode().strip()
    assert not git("diff", "--name-only", core, work_source, "--", "src", ":!"+str(fixture))
    text = fixture.read_text()
    before = git("show", f"{plan['source']}:{fixture}").decode()
    cases = set(re.findall(r"@Test\s+void (\w+)\(", text))
    assert cases == set(old_suite["exactMethods"]) and len(cases) == 10
    assert fixture.read_bytes() == git("show", f"{work_source}:{fixture}")
    unaffected = "  @Test\n  void monPipe002"
    assert before[before.index(unaffected):] == text[text.index(unaffected):]
    raw_cc, = OPS.glob("PG31432-*/compile.json")
    deps = read(raw_cc)["dependencies"]
    assert all(pin(Path(p["path"])) == p for p in deps)
    raw_cp = os.pathsep.join(p["path"] for p in deps)
    out = OPS / run_id
    out.mkdir()
    private = Path.cwd().parent / "pgpt-runs/PG379" / run_id
    private.mkdir(mode=0o700)
    steps = []

    def run(stage, *values):
        cmd = list(map(str, values))
        result = subprocess.run(cmd, capture_output=True, timeout=65,
                                env={"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"})
        (private/(stage+".stdout")).write_bytes(result.stdout)
        (private/(stage+".stderr")).write_bytes(result.stderr)
        steps.append(dict(stage=stage, command=cmd, exit=result.returncode, terminalAtUTC=utc(),
                          stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr)))
        assert result.returncode == 0, stage
        return result.stdout

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-observation-value-") as name:
        root = Path(name)
        prod, tests, analyzer = (root / part for part in ("prod", "test", "analyzer"))
        javac = JAVA.with_name("javac")
        strict = [javac, "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none"]
        f = SDK / "google-java-format-1.36.1-all-deps.jar"
        c = SDK / "static-gates-20261015/checkstyle-14.3.0-all.jar"
        run("format", JAVA, "-jar", f, "--skip-reflowing-long-strings", "--dry-run",
            "--set-exit-if-changed", fixture)
        style = private / "checkstyle.xml"
        run("checkstyle", JAVA, "-jar", c, "-c", "tools/quality/static/checkstyle.xml",
            "-f", "xml", "-o", style, fixture)
        assert not ET.parse(style).getroot().findall(".//error")
        run("main-compile", *strict, "-cp", SPECIFY, "-d", prod, *main_sources)
        targets = [NAMESPACE + type_name + ".class" for type_name in ("ObservationContext", "MonitoringPolicyEngine")]
        batch = Path(package["batchArtifact"]["path"])
        assert pin(batch) == package["batchArtifact"]
        with ZipFile(batch) as artifact:
            verified = [dict(classPath=member, sha256=sha(artifact.read(member))) for member in targets]
        for row in verified:
            assert pin(prod / row["classPath"])["sha256"] == row["sha256"]
        run("fixture-compile", *strict, "-cp", f"{prod}:{JUNIT}:{SPECIFY}", "-d", tests, fixture)
        xml_dir, data = private / "junit", private / "unit.exec"
        method_session = "PG41080"
        cls = NAMESPACE.replace("/", ".") + "MonitoringPolicyEngineTest"
        run("unit", JAVA, f"-javaagent:{AGENT}=destfile={data},sessionid={method_session},append=false",
            "-jar", JUNIT, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
            "--class-path", f"{prod}:{tests}:{SPECIFY}", "--select-class", cls, "--reports-dir", xml_dir)
        xml_file = xml_dir / "TEST-junit-jupiter.xml"
        suite = ET.parse(xml_file).getroot()
        xml_cases = [(t.attrib["classname"], t.attrib["name"].removesuffix("()"))
                     for t in suite.findall("testcase")]
        assert len(xml_cases) == 10 and set(xml_cases) == {(cls, method) for method in cases}
        assert [int(suite.attrib[k]) for k in ("tests", "failures", "errors", "skipped")] == [10, 0, 0, 0]
        measurement = root / "UnfilteredCodeMeasurement.java"
        measurement.write_bytes(git("show", RAW))
        run("raw-compile", *strict, "-cp", raw_cp, "-d", analyzer, measurement)
        record = run("raw", JAVA, "-cp", f"{analyzer}:{raw_cp}",
                     "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                     data, *[prod / member for member in targets])
        raw = out / "unfiltered.tsv"
        raw.write_bytes(record)
        decoder_source = git("show", DECODER)
        decoder = {}
        exec(compile(decoder_source, DECODER, "exec"), decoder)
        stream = decoder["decode"](data.read_bytes(), {name.removesuffix(".class") for name in targets})
        assert stream["sessions"][0]["labelBytesHex"] == method_session.encode().hex()
        raw_rows = []
        for line in record.decode().splitlines():
            cells = line.split("\t")
            if cells[0] == "CLASS":
                member = cells[1]
                assert cells[3] == "true"
                assert int(cells[2], 16) == int(stream["classes"][member]["crc64"], 16)
                counters = {kind: dict(missed=int(miss), covered=int(hit))
                            for kind, miss, hit in (r.split(":") for r in cells[6:])}
                assert all(v["missed"] == 0 for v in counters.values())
                raw_rows.append(dict(name=member, crc64=cells[2], counters=counters))
        assert len(raw_rows) == 2
        raw_context = next(row["counters"] for row in raw_rows if row["name"].endswith("/ObservationContext"))
        assert raw_context["METHOD"]["covered"] == 7 and raw_context["INSTRUCTION"]["covered"] == 51
    receipt = out / "manifest.json"
    with receipt.open("x") as f:
        json.dump(dict(actualExit=0, productionCore=core, fixtureSource=work_source, exactTests=sorted(cases),
                       extendedCase="PT-OPS-MONPIPE-001", newTestDefinitions=0, tests=10, errors=0,
                       failures=0, skipped=0, notRun=0, session=method_session, raw=raw_rows,
                       currentBatchClassBytes=verified, priorMissingMethods=2, priorMissingInstructions=6,
                       measuredClasses=2, otherClassCoverageClaimed=0, unchangedFixtureTests=9,
                       fixture=pin(fixture), mainSourcePins=[pin(p) for p in main_sources],
                       xmlOriginal=pin(xml_file), execOriginal=pin(data), rawOriginal=pin(raw),
                       independentDecoderSha256=sha(decoder_source), steps=steps, externalOperations=0,
                       oldExecsCombined=0, whole451=False, formalDelta=0, terminalAtUTC=utc()),
                  f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(pin(receipt), raw_context)


if __name__ == "__main__":
    main()
