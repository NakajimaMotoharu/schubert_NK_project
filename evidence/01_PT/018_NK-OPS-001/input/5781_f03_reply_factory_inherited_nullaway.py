"""Apply the current parent compiler policy to the reply factory's exact scoped source."""

import json
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve()
SUPPORT = runpy.run_path(str(HERE.with_name("5778_f03_config_main_typed_current.py")))
ROOT, OPS, PLANS = (SUPPORT[name] for name in ("ROOT", "OPS", "PLANS"))
pin, read, git, now, check_flags = (SUPPORT[name] for name in ("pin", "read", "git", "now", "check_flags"))
BASE = SUPPORT["BASE"]
PACKAGE = "dev/codex/schubert/nk/api/messaging/outbound"


def isolated_dependency(group, name, version, path):
    return (
        f"    <dependency><groupId>{group}</groupId><artifactId>{name}</artifactId>"
        f"<version>{version}</version><scope>system</scope><systemPath>{path}</systemPath></dependency>\n"
    )


def main():
    checkpoint, = PLANS.glob("3409_*")
    record = read(checkpoint)
    group = record["values"]
    source, core = group["source"], group["productionCoreMain"]
    assert git("rev-parse", "HEAD").decode().strip() == source
    program = Path("evidence/01_PT/005_NK-MSG-001/evidence")
    selected, = program.glob("PG43130*-v2/manifest.json")
    artifact = read(selected)
    assert artifact["actualExit"] == 0 and artifact["productCore"] == core
    assert artifact["attempts"][-1]["ordinary"] == 9
    dynamic = Path(artifact["attempts"][-1]["terminal"]["path"])
    assert pin(dynamic) == artifact["attempts"][-1]["terminal"]
    begin = dynamic.with_name("begin.json")
    assert pin(begin) in artifact["genuineOriginal"]
    begin_state = read(begin)
    jms, = (x for x in begin_state["borrowedVendorArtifacts"] if "jakarta.jms-api" in x["path"])
    assert pin(Path(jms["path"])) == jms
    protocol = artifact["protocol"]
    assert pin(Path(protocol["path"])) == protocol
    main = Path(artifact["production"]["path"])
    assert main.name == "JmsMessageFactory.java" and pin(main) == artifact["production"]
    member_sources = (main, main.with_name("package-info.java"))
    pom = git("show", f"{core}:pom.xml")
    assert pom == git("show", f"{source}:pom.xml") == (ROOT/"pom.xml").read_bytes()
    group_pom = BASE["HARNESS_POM"].replace("pgpt-outbox-nullaway-scope", "pgpt-reply-factory-nullaway-scope")
    group_pom = group_pom.replace(
        "  </dependencies>",
        isolated_dependency("dev.codex.schubert", "schubert-nk-protocol", "0.1.0-SNAPSHOT", protocol["path"])
        + isolated_dependency("jakarta.jms", "jakarta.jms-api", "3.1.0", jms["path"])
        + "  </dependencies>",
    )
    raw = ROOT.parent/"pgpt-runs/PG379"/group["run"]
    raw.mkdir(mode=0o700)
    out = OPS / group["run"]
    out.mkdir()
    started = now()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-reply-factory-typed-") as directory:
        work = Path(directory)
        project, home = work/"scope", work/"home"
        home.mkdir()
        (work/"pom.xml").write_bytes(pom)
        dest = project/"src/main/java"/PACKAGE
        dest.mkdir(parents=True)
        for path in member_sources:
            body = git("show", f"{core}:{path}")
            assert body == git("show", f"{source}:{path}") == path.read_bytes()
            (dest/path.name).write_bytes(body)
        isolated = project/"pom.xml"
        isolated.write_text(group_pom)
        maven, jdk = BASE["MAVEN"], BASE["JDK"]
        cmd = [str(maven), "-o", "-B", "-ntp", "-N", "-X", "-f", str(isolated),
               f"-Dmaven.repo.local={BASE['TOOLS'] / 'm2/repository'}", "-Dmaven.test.skip=true", "compile"]
        proc = subprocess.run(cmd, cwd=project, capture_output=True, timeout=80, check=False,
                              env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": str(home),
                                   "JAVA_HOME": str(jdk), "MAVEN_SKIP_RC": "true",
                                   "MAVEN_OPTS": f"-Duser.home={home} -Djava.io.tmpdir={work}"})
        (raw/"compile.stdout").write_bytes(proc.stdout)
        (raw/"compile.stderr").write_bytes(proc.stderr)
        lines = proc.stdout.decode("utf-8", errors="replace").splitlines()
        classes = project/"target/classes"
        built = {path.relative_to(classes).as_posix(): pin(path)["sha256"] for path in classes.rglob("*.class")}
        explicit = {f"{PACKAGE}/JmsMessageFactory.class", f"{PACKAGE}/package-info.class"}
        evidence = read(dynamic)["physical"]["sha256"]
        controls = dict(
            typedCompiler=check_flags(lines),
            exactlyTwoInputs=any("Compiling 2 source files" in line for line in lines),
            exactPhysicalMembers=set(built)==explicit,
            sameFactoryBytes=built.get(f"{PACKAGE}/JmsMessageFactory.class")==evidence,
            mavenSuccess=proc.returncode==0 and any("BUILD SUCCESS" in line for line in lines),
        )
    manifest = dict(run=group["run"], source=source, productCore=core, startEvent=record["eventId"],
        actualExit=0 if all(controls.values()) else 1, mavenExit=proc.returncode,
        startedAtUTC=started, terminalAtUTC=now(), wbs="WBS-F03/2-2-b", controls=controls,
        sourceInputs=list(map(pin, member_sources)), exactDependencies=[protocol,jms],
        outputPhysical=[dict(classFile=p,sha256=h) for p,h in sorted(built.items())],
        previousExactOrdinary=pin(selected), privateReceipts=[pin(raw/"compile.stdout"),pin(raw/"compile.stderr")],
        command=cmd, testReplay=0, actualBrokerOrService=0, whole451=False, formalAcceptanceId=None)
    with (out/"manifest.json").open("x") as report:
        report.write(json.dumps(manifest,indent=2)+"\n")
    print(controls)
    return manifest["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
