"""Apply the approved root compiler to exactly the current API monitoring unit closure."""
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git_read(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], timeout=15)


pmo = Path("documents/400_PGPT/470_PMO")
start = json.loads(next(pmo.glob("601_*/1380_*")).read_bytes())
ctx = start["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(row["path"])) == row for row in refs)
unit, close, prior = [json.loads(Path(row["path"]).read_bytes()) for row in refs[1:]]
assert unit["actualExit"] == close["actualExit"] == prior["steps"]["maven"]["exit"] == 0
prior_post_path = next(Path(refs[1]["path"]).parent.parent.glob("PG40882-*/manifest.json"))
prior_post = json.loads(prior_post_path.read_bytes())
assert prior_post["actualExit"] == 0 and prior_post["staticCommandsReplayed"] == 0
source = ctx["productionCoreMain"]
assert source == unit["source"] == close["source"] == prior["source"]
main = [row for row in unit["inputPins"] if "/src/main/" in row["path"]]
power = ("TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec",
         "WebStartupException")
assert len(main) == 23 and all("/schubert-nk-api/src/main/" in row["path"] for row in main)
assert all(sha(git_read(source, row["path"])) == row["sha256"] and pin(Path(row["path"])) == row
           for row in main)
assert not any(held.encode() in Path(row["path"]).read_bytes() for held in power for row in main)
parent = git_read(source, "pom.xml")
assert sha(parent) == prior["parentPomSha256"] and parent == Path("pom.xml").read_bytes()
dependencies = [row for row in unit["dependencyPins"]
                if Path(row["path"]).name != "junit-platform-console-standalone-1.13.4.jar"]
assert len(dependencies) == 15 and all(pin(Path(row["path"])) == row for row in dependencies)
tc = Path("../toolchain").resolve()
jdk = tc / "jdk-25.0.4"
m2 = tc / "m2/repository"
tool = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
context = {}
physical = []
target_join = None
rule_findings = []
opened = datetime.now(timezone.utc).isoformat()
environment = {"PATH": f"{jdk}/bin:{os.defpath}", "JAVA_HOME": str(jdk), "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40946-typed-") as tmp:
    top = Path(tmp)
    project = top / "scope"
    project.mkdir()
    (top / "pom.xml").write_bytes(parent)
    local = "".join(
        '<dependency><groupId>fixed.sdk</groupId>'
        f'<artifactId>local-sdk-{i}</artifactId><version>1</version><scope>system</scope>'
        f'<systemPath>{escape(row["path"])}</systemPath></dependency>'
        for i, row in enumerate(dependencies))
    pom = project / "pom.xml"
    pom.write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>local-api-monitoring-qualification</artifactId>'
        f'<dependencies>{local}</dependencies></project>\n')
    harness = pin(pom)
    src = project / "src/main/java"
    source_names = set()
    for row in main:
        relative = row["path"].split("/src/main/java/", maxsplit=1)[1]
        target = src / relative
        assert relative not in source_names
        source_names.add(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(row["path"]).read_bytes())
    command = list(map(str, [tool, "-o", "-B", "-ntp", "-N", "-X", "-f", pom,
                            f"-Dmaven.repo.local={m2}", "compile"]))
    result = subprocess.run(command, env=environment, capture_output=True, check=False, timeout=80)
    log = result.stdout.decode(errors="replace")
    context = {marker: marker in log for marker in (
        "-Xep:NullAway:ERROR", "-XepOpt:NullAway:JSpecifyMode=true", "-Werror", "Compiling 23 source files")}
    rule_findings = [line.strip() for line in log.splitlines() if "[NullAway]" in line]
    output = project / "target/classes"
    if result.returncode == 0 and all(context.values()):
        for path in sorted(output.rglob("*.class")):
            name = str(path.relative_to(output))
            assert name.removesuffix(".class").split("$", maxsplit=1)[0] + ".java" in source_names
            physical.append(dict(classPath=name, sha256=sha(path.read_bytes())))
        target, = (row for row in physical if row["classPath"].endswith("/ApiMetricHttpHandler.class"))
        target_join = dict(typed=target, executed=unit["coverage"]["target"],
                           exactClassBytes=target["sha256"] == unit["coverage"]["target"]["sha256"])
    if result.returncode != 0:
        print("\n".join(line for line in log.splitlines() if line.startswith("[ERROR]"))[-3200:])
ok = result.returncode == 0 and all(context.values()) and not rule_findings and bool(physical)
report = dict(actualExit=0 if ok else 1, compilerExit=result.returncode, source=source,
              startEvent=start["eventId"], startedAtUTC=opened,
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), command=command,
              controls=context, runtimeTestsExecuted=0, explicitSourcePins=main,
              dependencies=dependencies, parentPomSha256=sha(parent), harnessPom=harness,
              priorCompilerIndependent=pin(prior_post_path),
              priorPreparationAttempt=dict(exit=1, compilerStarted=False, bug="BUG-3427"),
              compilerStdoutSha256=sha(result.stdout), compilerStderrSha256=sha(result.stderr),
              nullAwayFindings=len(rule_findings), generatedPhysical=physical, targetJoin=target_join,
              externalActions=0, heldSourcesProvided=0, wholeF03=False, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
print(report["actualExit"], len(physical), report["nullAwayFindings"], target_join)
raise SystemExit(report["actualExit"])
