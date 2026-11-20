"""Qualify the exact LoginAccount storage value with the complete synthetic fixture."""
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def utc():
    return datetime.now(timezone.utc).isoformat()


def write(path, record):
    with path.open("x") as out:
        out.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def main():
    plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1425_*.json"))
    group = json.loads(plan.read_bytes())
    ctx = group["values"]
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    ops = Path("evidence/01_PT/018_NK-OPS-001")
    prior = json.loads(Path(ctx["oracleReferences"][2]["path"]).read_bytes())
    assert prior["actualExit"] == 0
    base = "dev/codex/schubert/nk/api/"
    module = Path("src/schubert-nk-api/src")
    account = module / ("main/java/" + base + "security/LoginAccount.java")
    root = account.parent
    typed_paths = [account, *(root / (name + ".java") for name in (
        "AuthenticatedActor", "LoginAttemptKind", "LoginAttemptState", "package-info")),
        root.parent / "domain/Role.java", root.parent / "domain/package-info.java"]
    fixture_support = [root / (name + ".java") for name in (
        "LockedLoginAttempt", "LoginAuditReason", "LoginResult",
        "LoginUsername", "IssuedContext", "AuthContextIdentity")]
    test = module / ("test/java/" + base + "security/LoginValueContractTest.java")
    paths = [*typed_paths, *fixture_support, test]
    proto_ref = ctx["oracleReferences"][3]
    proto_manifest = Path(proto_ref["path"])
    assert pin(proto_manifest) == proto_ref
    built = json.loads(proto_manifest.read_bytes())
    assert built["actualExit"] == 0
    protocol_pin = built["packaged"]["protocol"]
    protocol = Path(protocol_pin["path"])
    assert pin(protocol)["sha256"] == protocol_pin["sha256"]
    assert not subprocess.check_output(["git", "diff", "--name-only", built["source"],
                                        source, "--", "pom.xml", "src/schubert-nk-protocol"])
    for path in paths:
        assert subprocess.check_output(["git", "show", f"{source}:{path}"]) == path.read_bytes()
    names = subprocess.check_output(["git", "diff", "--name-only", ctx["source"], source, "--", "src"],
                                    text=True).splitlines()
    assert set(names) == {str(account), str(test)}

    tc = Path("../toolchain").resolve()
    jdk = tc / "jdk-25.0.4"
    java, javac = jdk / "bin/java", jdk / "bin/javac"
    cstyle = tc / "static-gates-20261015/checkstyle-14.3.0-all.jar"
    format_jar = tc / "google-java-format-1.36.1-all-deps.jar"
    junit = tc / "junit-platform-console-standalone-1.13.4.jar"
    agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    work = Path("../pgpt-runs/PG379").resolve() / ctx["run"]
    work.mkdir(mode=0o700)
    steps = []
    env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}

    def run(name, argv, allowed=(0,)):
        command = list(map(str, argv))
        start = utc()
        result = subprocess.run(command, env=env, capture_output=True, timeout=90, check=False)
        stdout, stderr = work / f"{name}.stdout", work / f"{name}.stderr"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        record = dict(step=name, exitCode=result.returncode, command=command, startedAtUTC=start,
                      terminalAtUTC=utc(), stdout=pin(stdout), stderr=pin(stderr))
        steps.append(record)
        write(work / f"{name}-terminal.json", record)
        if result.returncode not in allowed:
            raise SystemExit(result.returncode)
        return result.stdout

    run("format", [java, "-jar", format_jar, "--dry-run", "--set-exit-if-changed", *paths])
    report = run("checkstyle", [java, "-jar", cstyle, "-c", "tools/quality/static/checkstyle.xml",
                                "-f", "xml", *paths])
    assert not ET.fromstring(report).findall("file/error")
    top_pom = Path("pom.xml")
    (work / "pom.xml").write_bytes(top_pom.read_bytes())
    sub = work / "scope"
    sub.mkdir()
    (sub / "pom.xml").write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>login-storage-utf8-value-scope</artifactId><dependencies>'
        '<dependency><groupId>org.jspecify</groupId><artifactId>jspecify</artifactId></dependency>'
        '</dependencies></project>\n'
    )
    for p in typed_paths:
        target = sub / "src/main/java" / str(p).split("/src/main/java/", 1)[1]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(p.read_bytes())
    maven = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    log = run("typed", [maven, "-o", "-N", "-B", "-ntp", "-X", "-f", sub / "pom.xml",
                         f"-Dmaven.repo.local={tc}/m2/repository", "compile"])
    assert all(key in log for key in (b"-Xep:NullAway:ERROR", b"-Werror", b"Compiling 7 source files"))
    assert b"[NullAway]" not in log
    classes = sub / "target/classes"
    old = work / "before/LoginAccount.java"
    old.parent.mkdir()
    old.write_bytes(subprocess.check_output(["git", "show", f"{ctx['productionCoreMain']}:{account}"]))
    old_classes = work / "old-classes"
    run("before-compile", [javac, "--release", "25", "-g", "-proc:none", "-sourcepath", "",
                           "-cp", classes, "-d", old_classes, old])
    qualified = classes / (base + "security/LoginAccount.class")
    abi = [jdk / "bin/javap", "-public", "-s"]
    assert run("before-abi", [*abi, old_classes / qualified.relative_to(classes)]) == run(
        "candidate-abi", [*abi, qualified])
    tests = work / "tests"
    run("compile-test", [javac, "--release", "25", "-g", "-Xlint:all", "-Werror",
                          "-proc:none", "-implicit:none", "-sourcepath", "", "-cp",
                          f"{classes}:{junit}:{protocol}", "-d", tests, *fixture_support, test])
    owner = base.replace("/", ".") + "security.LoginValueContractTest"
    exec_data, reports = work / "unit.exec", work / "reports"
    session = "PG40976-LOGIN-STORAGE-FIVE"
    run("unit", [java, f"-javaagent:{agent}=destfile={exec_data},sessionid={session},append=false",
                 "-jar", junit, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                 "--class-path", f"{classes}:{tests}:{protocol}", "--select-class", owner, "--reports-dir", reports])
    receipt = reports / "TEST-junit-jupiter.xml"
    jxml = ET.parse(receipt).getroot()
    counts = {k: int(jxml.attrib[k]) for k in ("tests", "failures", "errors", "skipped")}
    expected = set(re.findall(r"@Test\s+void (\w+)\(", test.read_text()))
    actual = {p.attrib["name"].removesuffix("()") for p in jxml.findall("testcase")}
    assert counts == dict(tests=5, failures=0, errors=0, skipped=0) and expected == actual
    historical = {r["name"].removesuffix("()") for r in prior["cases"] if r["classname"] == owner}
    assert actual - historical == {"value005AccountStorageRequiresUtf8ScalarsAndPreservesExactBoundaryText"}

    proof = next((ops / "evidence").glob("PG40942*v2/raw-manifest.json"))
    raw = json.loads(proof.read_bytes())
    raw_source = work / "UnfilteredCodeMeasurement.java"
    raw_source.write_bytes(subprocess.check_output(
        ["git", "show", "c5674055a6:tools/quality/jacoco/UnfilteredCodeMeasurement.java"]))
    ref = json.loads(next((ops / "evidence").glob("PG40904*/manifest.json")).read_bytes())
    assert pin(raw_source)["sha256"] == ref["unfilteredToolSha256"]
    cc = raw["compileCommand"]
    libraries = cc[cc.index("-cp") + 1]
    measure = work / "measure"
    run("raw-compile", [*cc[:cc.index("-d")], "-d", measure, raw_source])
    target = qualified
    assert {str(p.relative_to(classes)) for p in classes.rglob("*.class")} == {
        str(p).split("/src/main/java/", 1)[1].removesuffix(".java") + ".class" for p in typed_paths
    }
    table = run("raw", [java, "-cp", f"{measure}:{libraries}", raw["rawCommand"][3], exec_data, target])

    observed = {}
    for line in table.decode().splitlines():
        if not line.startswith("CLASS\t"):
            continue
        row = line.split("\t")
        assert row[3] == "true"
        observed[row[1]] = dict(crc64=row[2], counters=[
            dict(kind=k, missed=int(m), covered=int(c))
            for k,m,c in (item.split(":") for item in row[6:])])
    assert len(observed) == 1
    output = ops / "evidence" / ctx["run"]
    output.mkdir()
    (output / "unfiltered.tsv").write_bytes(table)
    known = json.loads(next((ops / "evidence").glob("PG40880*/manifest.json")).read_bytes())
    sb, pmd = output / "spotbugs.xml", output / "pmd.xml"
    jspecify = tc / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
    aux = f"{classes}:{jspecify}"
    run("spotbugs", [java, "-Xmx1g", "-cp", known["steps"]["spotbugs"]["command"][3],
                     "edu.umd.cs.findbugs.FindBugs2", "-effort:max", "-low", "-xml:withMessages",
                     "-exitcode", "-auxclasspath", aux, "-output", sb, target], allowed=(0, 1))
    run("pmd", [java, "-cp", known["steps"]["pmd"]["command"][2], "net.sourceforge.pmd.cli.PmdCli",
                "check", "--dir", account, "--rulesets", "tools/quality/static/pmd.xml",
                "--use-version", "java-25", "--aux-classpath", f"{aux}:{jdk}/lib/jrt-fs.jar",
                "--no-cache", "--format", "xml", "--report-file", pmd], allowed=(0, 4))
    sbx, pmx = ET.parse(sb).getroot(), ET.parse(pmd).getroot()
    sb_findings = len(sbx.findall(".//BugInstance"))
    sb_errors = len(sbx.findall(".//Error")) + len(sbx.findall(".//MissingClass"))
    ns = {"p": "http://pmd.sourceforge.net/report/2.0.0"}
    pmd_findings = len(pmx.findall("p:file/p:violation", ns))
    pmd_errors = len(pmx.findall("p:error", ns))
    assert [x.attrib["class"] for x in sbx.findall(".//ClassStats")] == [base.replace("/", ".") + "security.LoginAccount"]
    passed = (not any((sb_findings, sb_errors, pmd_findings, pmd_errors))
              and all(c["missed"] == 0 for row in observed.values() for c in row["counters"]))
    write(output / "manifest.json", dict(
        source=source, beforeSource=ctx["productionCoreMain"], startEvent=group["eventId"], run=ctx["run"],
        actualExit=0 if passed else 1, terminalAtUTC=utc(), java="25.0.4", maven="3.9.12", os="Linux",
        testId="PT-LOGIN-VALUE005",
        inputs=[pin(p) for p in paths], rootPom=pin(top_pom), schemaPOM=pin(sub / "pom.xml"),
        fixtureSpec=pin(next(ops.glob("5531_*.md"))), previousCases=ctx["oracleReferences"][2],
        testCounts=counts, exactMethods=sorted(actual), steps=steps, nullAwayFindings=0,
        observed=observed, physical=[pin(p) for p in sorted(classes.rglob("*.class"))], junitXml=pin(receipt), session=session,
        execData=pin(exec_data), table=pin(output / "unfiltered.tsv"), newTests=1,
        requiredRegressions=4, unchangedPublicAbi=True, protocolCompileAndTestOnly=protocol_pin,
        spotBugs=dict(findings=sb_findings, errors=sb_errors, report=pin(sb)),
        pmd=dict(findings=pmd_findings, errors=pmd_errors, report=pin(pmd)), actualExternalOperations=0, wholeF03=False, whole451=False, formalDelta=0,
    ))
    print(counts, observed, sb_findings, sb_errors, pmd_findings, pmd_errors)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
