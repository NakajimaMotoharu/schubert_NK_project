"""Independent positive and negative dependency graphs for the existing Maven Enforcer rule."""
import json
import os
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def write(path, data):
    with path.open("x") as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


group = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1416_*.json")).read_bytes())
values = group["values"]
root = Path("pom.xml")
assert pin(root) == values["oracleReferences"][1]
assert root.read_bytes() == subprocess.check_output(
    ["git", "show", f"{values['productionCoreMain']}:pom.xml"]
)
tc = Path("../toolchain").resolve()
jdk = tc / "jdk-25.0.4"
maven = tc / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
repo = tc / "m2/repository"
work = Path("../pgpt-runs/PG379").resolve() / values["run"]
work.mkdir(mode=0o700)
(work / "pom.xml").write_bytes(root.read_bytes())
environment = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8"}
graph_metadata = [repo / (coordinate + ".pom") for coordinate in (
    "org/apache/commons/commons-compress/1.28.0/commons-compress-1.28.0",
    "commons-codec/commons-codec/1.19.0/commons-codec-1.19.0",
    "commons-codec/commons-codec/1.22.1/commons-codec-1.22.1",
)]
assert all(p.is_file() for p in graph_metadata)
results = []
for name, direct, expected in [("aligned", "1.19.0", 0), ("conflicting", "1.22.1", 1)]:
    model = work / name / "pom.xml"
    model.parent.mkdir()
    body = (
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
        '<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>'
        '<version>0.1.0-SNAPSHOT</version><relativePath>../pom.xml</relativePath></parent>'
        '<artifactId>independent-convergence-vector</artifactId><packaging>pom</packaging>'
        '<dependencies><dependency><groupId>org.apache.commons</groupId>'
        '<artifactId>commons-compress</artifactId><version>1.28.0</version></dependency>'
        '<dependency><groupId>commons-codec</groupId><artifactId>commons-codec</artifactId>'
        f'<version>{direct}</version></dependency></dependencies></project>\n'
    )
    model.write_text(body)
    command = list(map(str, [maven, "-B", "-ntp", "-o", "-N", "-f", model,
                             f"-Dmaven.repo.local={repo}", "validate"]))
    started = utc()
    proc = subprocess.run(command, env=environment, capture_output=True, timeout=50, check=False)
    output = model.parent / "maven.stdout"
    output.write_bytes(proc.stdout)
    record = dict(fixture=name, directCodecVersion=direct, expectedExit=expected, actualExit=proc.returncode,
                  command=command, terminalAtUTC=utc(), startedAtUTC=started, model=pin(model),
                  stdout=pin(output), stderrSha256=sha256(proc.stderr).hexdigest())
    write(model.parent / "terminal.json", record)
    log = proc.stdout.decode()
    common = all(rule + " passed" in log for rule in ("RequireJavaVersion", "RequireMavenVersion"))
    if expected == 0:
        proof = "DependencyConvergence passed" in log and "BUILD SUCCESS" in log
    else:
        proof = all(s in log for s in (
            "DependencyConvergence failed", "Dependency convergence error",
            "commons-codec:commons-codec:jar:1.19.0",
            "commons-codec:commons-codec:jar:1.22.1",
            "org.apache.commons:commons-compress:jar:1.28.0",
            "independent-convergence-vector",
        )) and "Could not resolve dependencies" not in log
    results.append(dict(**record, javaMavenVersionRulesPassed=common,
                        exactConvergenceOracle=proof, passState=proc.returncode == expected and common and proof))

evidence = Path("evidence/01_PT/018_NK-OPS-001")
out = evidence / "evidence" / values["run"]
out.mkdir()
passed = all(result["passState"] for result in results)
write(out / "manifest.json", dict(
    source=values["productionCoreMain"], run=values["run"], startEvent=group["eventId"],
    actualExit=0 if passed else 1, terminalAtUTC=utc(), testId="PT-F02-MAVEN-002",
    testSpec=pin(next(evidence.glob("5525_*.md"))), rootPom=pin(root), graphPoms=list(map(pin, graph_metadata)),
    tooling=dict(jdk="25.0.4", maven="3.9.12"), cases=results, productTests=0,
    productClassesReadOrCompiled=0, offline=True, outerArtifactOperations=0,
    previouslySuccessfulValidateRepeated=False, wholeF02=False, whole451=False, formalDelta=0,
))
print([(r["fixture"],r["actualExit"],r["javaMavenVersionRulesPassed"],r["exactConvergenceOracle"]) for r in results])
raise SystemExit(0 if passed else 1)
