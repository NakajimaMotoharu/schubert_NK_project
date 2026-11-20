"""Requalify the Web result mapper using the already admitted standalone error fixtures."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def pin(p):
    return dict(path=str(p), sha256=sha256(p.read_bytes()).hexdigest())


def load(p):
    return json.loads(p.read_bytes())


def utc():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], timeout=25)


def main():
    pmo = Path("documents/400_PGPT/470_PMO")
    group = load(next(pmo.glob("601_*/1503_*")))
    scope = group["values"]
    refs = scope["oracleReferences"]
    assert all(pin(Path(r["path"])) == r for r in refs)
    gap, original, original_raw, status = [load(Path(r["path"])) for r in refs[1:]]
    assert all(x["actualExit"] == 0 for x in (gap, original, original_raw, status))
    assert original["counts"] == dict(tests=22, errors=0, failures=0, skipped=0)
    source = git("rev-parse", "HEAD").decode().strip()
    owner = "dev/codex/schubert/nk/web/error/WebResultMapper"
    main_path = Path("src/schubert-nk-web/src/main/java") / (owner + ".java")
    changed = git("diff", "--name-only", scope["source"], source, "--", "src").decode().splitlines()
    assert changed == [str(main_path)] and main_path.read_bytes() == git("show", f"{source}:{main_path}")
    fixture = Path("tools/quality/architecture/ErrorValueContractTest.java")
    for x in original["qualifiedSourceInputs"]:
        p = Path(x["path"])
        if p not in (main_path, fixture):
            assert pin(p) == x
    status_fixture = status["testInput"] if "testInput" in status else status["fixture"]
    assert pin(fixture.resolve()) == status_fixture
    expected = Counter((x["className"], x["method"]) for x in original["passingCases"])
    class_name, method = status["selectedCase"].split("#")
    expected.update({(class_name, method + "()"): 1})
    assert len(expected) == 23

    original_command = original["unitCommand"]
    stored_cp = original_command[original_command.index("--class-path") + 1].split(":")
    original_work = Path(stored_cp[0]).parent
    sdk = list(map(Path, stored_cp[2:]))
    assert len(sdk) == 26 and all(p.is_file() for p in sdk)
    proto = Path(original["evaluatedCurrentProtocol"]["path"])
    assert proto == sdk[0] and pin(proto)["sha256"] == original["evaluatedCurrentProtocol"]["sha256"]
    prepared = load(next(Path("evidence/01_PT/018_NK-OPS-001/evidence").glob("PG28014*/manifest.json")))
    assert all(str(p) in prepared["dependencies"] and pin(p)["sha256"] == prepared["dependencies"][str(p)]
               for p in sdk[1:])
    cached = sdk[-1]
    with ZipFile(cached) as archive:
        assert not any(x.startswith(owner) for x in archive.namelist())

    tc = Path("../toolchain").resolve()
    jdk = tc / "jdk-25.0.4"
    java, javac, javap = [jdk / ("bin/" + tool) for tool in ("java", "javac", "javap")]
    junit = next(p for p in sdk if p.name == "junit-platform-console-standalone-1.13.4.jar")
    annotations = next(p for p in sdk if p.name == "jspecify-1.0.1.jar")
    agent = Path(original["tools"][2]["path"])
    assert pin(agent) == original["tools"][2]
    work = Path("../pgpt-runs/PG379").resolve() / scope["run"]
    work.mkdir(mode=0o700)
    testdir, products = work / "units", work / "products"
    removed = {f"products/{owner}.class", f"products/{owner}$1.class",
               f"units/{class_name.replace('.', '/')}.class"}
    retained = []
    for item in original["retainedClasses"]:
        p = Path(item["path"])
        assert pin(p) == item
        relative = p.relative_to(original_work)
        if str(relative) not in removed:
            new = work / relative
            new.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, new)
            retained.append(pin(new))
    assert len(retained) == 8
    temp = work / "tmp"
    temp.mkdir()
    env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8",
           "TZ": "Asia/Tokyo"}
    steps = []

    def run(name, argv, allowed=(0,)):
        cmd = list(map(str, argv))
        start = utc()
        result = subprocess.run(cmd, env=env, cwd=work, capture_output=True, timeout=90, check=False)
        stdout, stderr = [work / f"{name}.{suffix}" for suffix in ("stdout", "stderr")]
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        step = dict(name=name, command=cmd, exitCode=result.returncode, startedAtUTC=start,
                    terminalAtUTC=utc(), stdout=pin(stdout), stderr=pin(stderr))
        steps.append(step)
        (work / f"{name}-terminal.json").write_text(json.dumps(step, indent=2) + "\n")
        if result.returncode not in allowed:
            raise SystemExit(result.returncode)
        return result.stdout

    (work / "pom.xml").write_bytes(Path("pom.xml").read_bytes())
    module = work / "limited"
    staged = module / "src/main/java" / (owner + ".java")
    staged.parent.mkdir(parents=True)
    shutil.copyfile(main_path, staged)
    (module / "pom.xml").write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>web-result-mapper-limited</artifactId><dependencies>'
        '<dependency><groupId>org.jspecify</groupId><artifactId>jspecify</artifactId></dependency>'
        '<dependency><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk-protocol</artifactId>'
        f'<version>0.1.0-SNAPSHOT</version><scope>system</scope><systemPath>{proto}</systemPath>'
        '</dependency></dependencies></project>\n')
    maven = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    log = run("typed", [maven, "-o", "-N", "-B", "-ntp", "-X", "-f", module / "pom.xml",
                        f"-Dmaven.repo.local={tc}/m2/repository", "compile"])
    assert all(v in log for v in (b"-Xep:NullAway:ERROR", b"-Werror", b"Compiling 1 source file"))
    assert b"[NullAway]" not in log
    typed = module / "target/classes"
    target = products / (owner + ".class")
    typed_classes = list(typed.rglob("*.class"))
    assert typed_classes == [typed / (owner + ".class")]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(typed_classes[0], target)
    old_target = original_work / "products" / (owner + ".class")
    assert run("abi-old", [javap, "-public", "-s", old_target]) == run("abi-new", [javap, "-public", "-s", target])
    assert not (products / (owner + "$1.class")).exists()
    cp = ":".join(map(str, (products, testdir, *sdk)))
    run("test-compile", [javac, "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none",
                         "-implicit:none", "-sourcepath", "", "-cp", cp, "-d", testdir, fixture.resolve()])
    paths = [target if Path(row["path"]).stem == target.stem else Path(row["path"])
             for row in original_raw["targetClasses"] if not row["path"].endswith("WebResultMapper$1.class")]
    assert len(paths) == 6
    for p in paths:
        if p != target:
            assert pin(p) in original_raw["targetClasses"]

    out = Path("evidence/01_PT/016_NK-WEB-002/evidence") / scope["run"]
    out.mkdir()
    rules = Path("tools/quality/static").resolve()
    source_path = main_path.resolve()
    run("format", [java, "-jar", tc / "google-java-format-1.36.1-all-deps.jar",
                   "--dry-run", "--set-exit-if-changed", source_path])
    style = run("style", [java, "-jar", tc / "static-gates-20261015/checkstyle-14.3.0-all.jar",
                          "-c", rules / "checkstyle.xml", "-f", "xml", source_path])
    assert not ET.fromstring(style).findall(".//error")
    (out / "checkstyle.xml").write_bytes(style)
    gate = load(next(Path("evidence/01_PT/018_NK-OPS-001/evidence").glob("PG40880*/manifest.json")))
    spotbugs, pmd = [(out / f"{suffix}.xml").resolve() for suffix in ("spotbugs", "pmd")]
    aux = f"{typed}:{proto}:{annotations}"
    run("spotbugs", [java, "-Xmx1g", "-cp", gate["steps"]["spotbugs"]["command"][3],
        "edu.umd.cs.findbugs.FindBugs2", "-effort:max", "-low", "-xml:withMessages", "-exitcode",
        "-auxclasspath", aux, "-output", spotbugs, target])
    run("pmd", [java, "-cp", gate["steps"]["pmd"]["command"][2], "net.sourceforge.pmd.cli.PmdCli",
        "check", "--dir", source_path, "--rulesets", rules / "pmd.xml", "--use-version", "java-25",
        "--aux-classpath", f"{aux}:{jdk}/lib/jrt-fs.jar", "--no-cache",
        "--format", "xml", "--report-file", pmd], allowed=(0, 4))
    sb, px = [ET.parse(p).getroot() for p in (spotbugs, pmd)]
    assert not sb.findall(".//BugInstance") and not sb.findall(".//MissingClass") and not sb.findall(".//Error")
    assert [x.attrib["class"] for x in sb.findall(".//ClassStats")] == [owner.replace("/", ".")]
    actual_pmd = [[x.attrib.get(k) for k in ("rule", "beginline")]
                  for x in px.iter() if x.tag.endswith("}violation")]
    assert not any(x.tag.endswith("}error") for x in px.iter())

    session, stream = "PG41046-WEB-ERROR-MAPPER-23", work / "unit.exec"
    init, reports = work / "class-init.log", work / "reports"
    selection = [a for i, a in enumerate(original_command)
                 if a == "--select-class" or (i and original_command[i-1] == "--select-class")]
    assert len(selection) == 6
    run("unit", [java, f"-Djava.io.tmpdir={temp}", "-Dfile.encoding=UTF-8",
        "-Djunit.jupiter.execution.parallel.enabled=false", "-Djunit.jupiter.extensions.autodetection.enabled=false",
        f"-javaagent:{agent}=destfile={stream},sessionid={session},append=false",
        f"-Xlog:class+init=info:file={init}", "-jar", junit, "execute", "--disable-ansi-colors",
        "--class-path", cp, *selection, "--reports-dir", reports, "--fail-if-no-tests"])
    xml = reports / "TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    counts = {k: int(suite.attrib[k]) for k in ("tests", "failures", "errors", "skipped")}
    assert counts == dict(tests=23, failures=0, errors=0, skipped=0)
    assert Counter((e.attrib["classname"], e.attrib["name"]) for e in suite.iter("testcase")) == expected
    trace = init.read_bytes()
    assert all(label not in trace for label in
        (b"TemporaryInfrastructureException", b"FingerprintKeyRing", b"ResponseSnapshotCodec", b"WebStartupException"))
    raw_driver = load(next(Path("evidence/01_PT/018_NK-OPS-001/evidence").glob("PG38688*/manifest.json")))
    data = run("unfiltered", [*raw_driver["rawCommand"][:4], stream, *paths])
    table = out / "unfiltered.tsv"
    table.write_bytes(data)
    measured = {}
    for row in (line.split("\t") for line in data.decode().splitlines()):
        if row[0] == "CLASS":
            assert row[3] == "true" and row[1] not in measured
            measured[row[1]] = dict(crc=row[2], counters={
                k: dict(missed=int(m), covered=int(c))
                for k, m, c in (s.split(":") for s in row[6:])})
    assert len(measured) == 6 and owner in measured
    assert all(not c["missed"] for row in measured.values() for c in row["counters"].values())
    record = dict(actualExit=0, source=source, beforeSource=scope["productionCoreMain"],
                  startEvent=group["eventId"], terminalAtUTC=utc(), counts=counts, oldReferences=refs[1:],
                  sourceDelta=[pin(main_path)], publicAbiSame=True, sourceMainTypedCount=1, heldTypeActions=0,
                  retainedInputs=retained, physical=[pin(p) for p in paths], removedCompilerTypes=[owner+"$1"],
                  packageScopeMaven=False, session=session, xml=pin(xml), exec=pin(stream), raw=pin(table),
                  measured=measured, pmdOccurrences=actual_pmd, steps=steps, realBackendActions=0, whole451=False)
    (out / "manifest.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(counts, measured[owner], actual_pmd)


if __name__ == "__main__":
    main()
