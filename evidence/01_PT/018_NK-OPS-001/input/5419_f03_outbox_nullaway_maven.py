"""Compile the exact allowed Outbox sources with the inherited NullAway rules."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


ROOT = Path.cwd()
PLAN = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
SOURCE_DIR = Path("src/schubert-nk-api/src/main/java")
TYPES = {"OutboxRetrySchedule.java", "OutboxDispatchReport.java", "package-info.java"}
TOOLS = ROOT.parent / "toolchain"
JDK = TOOLS / "jdk-25.0.4"
MAVEN = TOOLS / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
HARNESS_POM = """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>dev.codex.schubert</groupId>
    <artifactId>schubert-nk</artifactId>
    <version>0.1.0-SNAPSHOT</version>
  </parent>
  <artifactId>pgpt-outbox-nullaway-scope</artifactId>
  <dependencies>
    <dependency><groupId>org.jspecify</groupId><artifactId>jspecify</artifactId></dependency>
  </dependencies>
</project>
"""


def sha(data):
    return sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    group = read(next(PLAN.glob("1058_F03*")))
    values = group["values"]
    assert all(sha(Path(row["path"]).read_bytes()) == row["sha256"] for row in values["oracleReferences"])
    source = git("rev-parse", "HEAD").decode().strip()
    assert source == values["source"]
    root_pom = git("show", f"{source}:pom.xml")
    assert root_pom == git("show", f'{values["productionCoreMain"]}:pom.xml')
    original = read(next(OPS.glob("PG40688-*/begin.json")))["sourceHashes"]
    assert {Path(path).name for path in original} == TYPES
    pins = {Path(path).relative_to(SOURCE_DIR): fingerprint for path, fingerprint in original.items()}
    out = OPS / values["run"]
    out.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-outbox-nullaway-") as temporary:
        work = Path(temporary)
        project = work / "scope"
        sources = project / "src/main/java"
        home = work / "isolated-home"
        home.mkdir()
        (work / "pom.xml").write_bytes(root_pom)
        for path, expected in pins.items():
            body = git("show", f"{source}:{SOURCE_DIR / path}")
            assert sha(body) == expected
            target = sources / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        pom = project / "pom.xml"
        pom.write_text(HARNESS_POM)
        command = list(map(str, (MAVEN, "-o", "-B", "-ntp", "-N", "-X", "-f", pom,
                                 f"-Dmaven.repo.local={TOOLS / 'm2/repository'}", "compile")))
        result = subprocess.run(command, cwd=project, capture_output=True, check=False, timeout=70,
                                env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": str(home),
                                     "JAVA_HOME": str(JDK), "MAVEN_SKIP_RC": "true",
                                     "MAVEN_OPTS": f"-Duser.home={home} -Djava.io.tmpdir={work}"})
        stdout = result.stdout.decode("utf-8", errors="replace")
        controls = {
            "nullAwayConfigured": "-Xep:NullAway:ERROR" in stdout,
            "jspecifyModeConfigured": "-XepOpt:NullAway:JSpecifyMode=true" in stdout,
            "warningsAsErrors": "-Werror" in stdout,
            "nullAwayArtifactResolved": "nullaway-0.14.1.jar" in stdout,
            "exactThreeInputsCompiled": "Compiling 3 source files" in stdout,
            "mavenBuildSuccessful": "BUILD SUCCESS" in stdout,
        }
        classes = project / "target/classes"
        physical = {str(path.relative_to(classes)): sha(path.read_bytes()) for path in classes.rglob("*.class")}
        expected = {str(path.with_suffix(".class")) for path in pins}
        okay = result.returncode == 0 and all(controls.values()) and set(physical) == expected
        evidence = dict(
            run=values["run"], startEvent=group["eventId"], source=source,
            lastQualifiedProductionCore=values["productionCoreMain"],
            actualExit=0 if okay else 1, mavenExit=result.returncode,
            command=command, rootPomSha256=sha(root_pom), harnessPomSha256=sha(pom.read_bytes()),
            inheritedNegativeCompilerEvidence=values["oracleReferences"][2],
            sourceHashes=original, physical=physical, controls=controls,
            mavenBinarySha256=sha(MAVEN.read_bytes()), jdkBinarySha256=sha((JDK / "bin/javac").read_bytes()),
            stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr),
            oldStaticReplayed=0, productTestsExecuted=0, newCoverage=0, formalDelta=0,
            wholeF03=False, whole451=False, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        )
        (out / "manifest.json").write_text(json.dumps(evidence, indent=2) + "\n")
        if not okay:
            failures = [line for line in stdout.splitlines() if "[ERROR]" in line]
            (out / "diagnostic.txt").write_text("\n".join(failures[:20]) + "\n")
        print({"mavenExit": result.returncode, "physical": len(physical), "controls": controls})
        return evidence["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
