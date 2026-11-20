"""Execute four ExpiryAudit proxy test classes against one exact packaged family."""

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


HERE = Path(__file__)
P = runpy.run_path(str(HERE.with_name("5417_f02_expiry_audit_jdbc_pt.py")))
POST = runpy.run_path(str(HERE.with_name("5418_f02_expiry_audit_jdbc_post.py")))
E, PLAN, JAVA, JUNIT, JSPECIFY, AGENT, PKG = (
    P[name] for name in ("E", "PLAN", "JAVA", "JUNIT", "JSPECIFY", "AGENT", "PKG")
)
pin, run, git = (P[name] for name in ("proof", "run", "git"))
TESTS = {
    "ExpiryAuditJdbcFailureGraphTest": 8,
    "ExpiryAuditResourceFailureTest": 4,
    "ExpiryAuditPortTest": 9,
    "ExpiryAuditPredicateContractTest": 5,
}
SUPPORT = ("JdbcResourceCases",)
FORBIDDEN = ("DriverManager", "BatchDatabaseFixture", "ProcessBuilder", "java.net.Socket",
             "LinuxDirectoryCalls", "LinuxInodeSecurity", "java.lang.foreign", "Class.forName")


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    event = read(next(PLAN.glob("1077_F03*")))
    v = event["values"]
    assert all(pin(row["path"]) == row for row in v["oracleReferences"])
    pkg, static, scoped = (read(row["path"]) for row in v["oracleReferences"][1:4])
    core = pkg["candidateProductionSource"]
    assert static["codeCandidate"] == core and pkg["verify"]["focusedPhysicalByteEqual"]
    assert scoped["actualExit"] == static["actualExit"] == 0
    assert v["source"] == git("rev-parse", "HEAD").decode().strip()
    assert not git("diff", "--name-only", core, v["source"], "--", "pom.xml", "src")
    out = (E / "PG40720-f03-expiry-current-26-proxy-v3").resolve()
    out.mkdir()
    runtime = out / "jacoco.exec"
    session = "PG40720-EXPIRY-AUDIT-SAME-26"
    dep_report = read(next(E.glob("PG40712-*/manifest.json")))
    family = dep_report["physicalHashes"]
    prefix = str(PKG).replace("/", ".")
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-current-expiry-exact-") as loc:
        root = Path(loc)
        main, tests, reports = (root / name for name in ("main", "tests", "reports"))
        for folder in (main, tests, reports):
            folder.mkdir()
        dep = P["make_classpath"](pkg["privateJars"], root / "deps")
        assert dep == dep_report["classpaths"]
        artifact = pkg["privateJars"]["batch"]["artifact"]
        assert pin(artifact["path"]) == artifact
        with ZipFile(artifact["path"]) as jar:
            for path, fingerprint in family.items():
                node = main / path
                node.parent.mkdir(parents=True, exist_ok=True)
                node.write_bytes(jar.read(path))
                assert pin(node)["sha256"] == fingerprint
        files = []
        inputs = {}
        for name in (*TESTS, *SUPPORT):
            path = P["BATCH"] / "test/java" / PKG / (name + ".java")
            body = git("show", f"{core}:{path}")
            assert body == path.read_bytes() and all(word.encode() not in body for word in FORBIDDEN)
            fixture = root / path.name
            fixture.write_bytes(body)
            inputs[str(path)] = pin(fixture)["sha256"]
            files.append(fixture)
        cp = os.pathsep.join(map(str, (main, root / "deps", JSPECIFY, JUNIT)))
        stages = {"testCompile": run("testCompile", [
            JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
            "-cp", cp, "-d", tests, *files], out, root)}
        cases, observed, coverage = [], Counter(), None
        if stages["testCompile"]["actualExit"] == 0:
            stages["unit"] = run("unit", [JAVA,
                f"-javaagent:{AGENT}=destfile={runtime},sessionid={session},append=false,"
                f"includes={prefix}.ExpiryAuditRepository*",
                "-Xmx512m", "-jar", JUNIT, "execute", "--disable-banner", "--disable-ansi-colors",
                "--class-path", f"{tests}{os.pathsep}{cp}", "--reports-dir", reports, "--fail-if-no-tests",
                *[f"--select-class={prefix}.{name}" for name in TESTS]], out, root)
        xml = reports / "TEST-junit-jupiter.xml"
        if xml.is_file():
            junit = ET.parse(xml).getroot()
            for node in junit.findall("testcase"):
                name = node.get("classname")
                assert name.startswith(prefix + ".")
                test = node.get("name")
                outcome = next((label for label in ("error", "failure", "skipped")
                                if node.find(label) is not None), "pass")
                observed[name.removeprefix(prefix + ".")] += 1
                cases.append(dict(testClass=name, name=test, outcome=outcome))
            (out / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
        if runtime.is_file() and cases:
            old = read(next(E.glob("PG40696-*-after/manifest.json")))
            raw = old["stages"]["unfiltered"]["command"][:4]
            stages["coverage"] = run("coverage", [*raw, runtime, *(main / name for name in sorted(family))], out, root)
            if stages["coverage"]["actualExit"] == 0:
                coverage = POST["counters"](out / "coverage.stdout", family)
        success = (len(stages) == 3 and all(step["actualExit"] == 0 for step in stages.values())
                   and observed == TESTS and all(row["outcome"] == "pass" for row in cases)
                   and len(cases) == len({(row["testClass"], row["name"]) for row in cases}) == 26)
    data = dict(actualExit=0 if success else 1, source=v["source"], candidateProductionSource=core,
                stages=stages, sourceInputs=inputs, physical=family, testClassCounts=observed, session=session,
                compileOnlyHelpers=list(SUPPORT),
                actualTests=len(cases), isolatedSameExec=coverage, previouslyScopedEightNotAddedToFormal=8,
                legacyCasesRequalifiedInWidenedScope=18, maxCoverage=True if coverage and all(
                    coverage[k]["missed"] == 0 for k in ("LINE", "METHOD", "CLASS", "BRANCH")) else False,
                actualExternalActions=0, realDataSource=False, originalProgramInputsUnchanged=True,
                wholeF03=False, whole451=False, newFormalAcceptance=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    (out / "manifest.json").write_text(json.dumps(data, indent=2) + "\n")
    print(dict(exits={key: value["actualExit"] for key, value in stages.items()},
               actualTests=len(cases), unfiltered=coverage))
    return data["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
