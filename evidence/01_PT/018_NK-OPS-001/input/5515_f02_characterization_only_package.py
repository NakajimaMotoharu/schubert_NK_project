"""Build the comparative-tool artifact using the pinned Maven reactor metadata."""
import hashlib
import io
import json
import os
import struct
import subprocess
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(content):
    return hashlib.sha256(content).hexdigest()


def write(path, record):
    with path.open("x") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    begin = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1389_*.json"))
    start = json.loads(begin.read_bytes())
    core, source = (start["values"][key] for key in ("productionCoreMain", "source"))
    prior_run = start["values"]["run"]
    run = prior_run.removesuffix("-v2") + "-v3"
    comparison = "program/characterization"
    root_pom = git("show", f"{source}:pom.xml")
    namespace = {"m": "http://maven.apache.org/POM/4.0.0"}
    modules = [node.text for node in ET.fromstring(root_pom).findall("m:modules/m:module", namespace)]
    if len(modules) != 7 or comparison not in modules or len(set(modules)) != 7:
        raise ValueError("unexpected Maven reactor member inventory")
    poms = [f"{module}/pom.xml" for module in modules]
    main_input = f"{comparison}/src/main"
    selection = ["pom.xml", *poms, main_input]
    path_names = git("ls-tree", "-r", "--name-only", source, "--", *selection).decode().splitlines()
    if len(path_names) != 14 or git("diff", "--name-only", core, source, "--", *selection):
        raise ValueError("comparison sources or Reactor model changed")
    bundle = git("archive", "--format=tar", source, "--", *selection)
    run_base = Path("../pgpt-runs/PG379").resolve()
    private = run_base / run
    private.mkdir(mode=0o700)
    stage = private / "source"
    stage.mkdir()
    with tarfile.open(fileobj=io.BytesIO(bundle)) as archive:
        archive.extractall(stage, filter="data")
    pins = []
    for name in path_names:
        content = (stage / name).read_bytes()
        if git("show", f"{source}:{name}") != content:
            raise ValueError(f"isolated source mismatch: {name}")
        pins.append(dict(path=name, sha256=sha(content)))

    toolchain = Path("../toolchain").resolve()
    jdk = toolchain / "jdk-25.0.4"
    m2 = toolchain / "m2/repository"
    mvn = toolchain / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    env = {**os.environ, "JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.environ['PATH']}"}
    command = [
        str(mvn), "-B", "-ntp", "-o", "-f", "pom.xml", f"-Dmaven.repo.local={m2}",
        "-pl", comparison, "-am", "-Dmaven.test.skip=true", "package",
    ]
    started_at = utc()
    code = None
    timeout = False
    try:
        with (private / "build.log").open("xb") as output:
            code = subprocess.run(
                command, cwd=stage, env=env, stdout=output, stderr=subprocess.STDOUT,
                timeout=90, check=False,
            ).returncode
    except subprocess.TimeoutExpired:
        timeout = True
    terminal_at = utc()
    terminal = private / "terminal.json"
    write(terminal, dict(source=source, run=run, command=command, startedAtUTC=started_at,
                         terminalAtUTC=terminal_at, actualExit=code, timedOut=timeout))
    if code != 0:
        raise SystemExit(code if code is not None else 124)

    logs = (private / "build.log").read_bytes()
    expectations = [b"BUILD SUCCESS", b"Not compiling test sources", b"Tests are skipped."]
    if any(value not in logs for value in expectations):
        raise ValueError("package exit not supported by the expected build records")
    if any((stage / module / "target").exists() for module in modules if module != comparison):
        raise ValueError("unexpected product reactor output")

    target = stage / comparison / "target"
    jar = target / "schubert-characterization-0.1.0-SNAPSHOT.jar"
    classes = []
    with zipfile.ZipFile(jar) as packaged:
        for name in sorted(packaged.namelist()):
            if not name.endswith(".class"):
                continue
            content = packaged.read(name)
            major = struct.unpack(">H", content[6:8])[0]
            if not name.startswith("dev/codex/schubert/characterization/"):
                raise ValueError(f"unexpected package entry: {name}")
            if content[:4] != bytes.fromhex("cafebabe") or major != 69:
                raise ValueError(f"classfile is not Java 25: {name}")
            if content != (target / "classes" / name).read_bytes():
                raise ValueError(f"jar/output mismatch: {name}")
            classes.append(dict(path=name, sha256=sha(content), classfileMajor=major))
    actual_names = sorted(str(p.relative_to(target / "classes")) for p in (target / "classes").rglob("*.class"))
    if not classes or [entry["path"] for entry in classes] != actual_names or len(set(actual_names)) != len(classes):
        raise ValueError("incomplete or duplicate classfile inventory")

    previous_terminal = run_base / prior_run / "terminal.json"
    previous = json.loads(previous_terminal.read_bytes())
    assert previous["source"] == source and previous["actualExit"] == 1
    published = Path("evidence/01_PT/018_NK-OPS-001/evidence") / run
    published.mkdir()
    java_version = next(line for line in (jdk / "release").read_text().splitlines() if line.startswith("JAVA_VERSION="))
    write(published / "manifest.json", dict(
        run=run, source=source, productionCore=core, startEvent=start["eventId"], wbs="WBS-F02-a",
        actualExit=code, startedAtUTC=started_at, terminalAtUTC=terminal_at,
        os=os.uname().sysname, architecture=os.uname().machine, java=java_version, maven="3.9.12",
        command=command, selectedMembers=["schubert-nk", "schubert-characterization"],
        productPomMetadataOnly=sorted(set(modules) - {comparison}),
        sourceArchiveSha256=sha(bundle), inputs=pins, productModulesPackagedHere=0,
        packagedClassCount=len(classes), classes=classes,
        jar=dict(path=str(jar), sha256=sha(jar.read_bytes()), bytes=jar.stat().st_size),
        buildLogSha256=sha(logs), privateTerminalSha256=sha(terminal.read_bytes()),
        testsExecuted=0, toolEntryPointsExecuted=0, characterizationCasesExecuted=0,
        baselineReadOrWrittenByBuild=False, externalOperations=0,
        preparationAttempts=[
            dict(version=1, reason="unregistered work category", mavenInvocations=0),
            dict(version=2, reason="absent sibling module POMs", mavenInvocations=1,
                 actualExit=previous["actualExit"], terminalSha256=sha(previous_terminal.read_bytes())),
        ],
        relatedDefect="BUG-3429", wholeF02=False, whole451=False, formalDelta=0,
    ))
    print("Comparison-only Maven package exit 0.", len(classes), "Java 25 classfiles.")


if __name__ == "__main__":
    main()
