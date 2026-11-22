"""Apply the current inherited compiler to the previously scoped settings sources."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


ROOT = Path.cwd()
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PLANS = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
BASE = runpy.run_path(str(Path(__file__).with_name("5419_f03_outbox_nullaway_maven.py")))
MAIN_FILES = {
    "ApiNonSecretConfig.java",
    "WebNonSecretConfig.java",
    "JdbcFailureGraph.java",
    "StorageIoException.java",
    "package-info.java",
}


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=25)


def now():
    return datetime.now(timezone.utc).isoformat()


def manifest(prefix):
    path, = OPS.glob(prefix + "*/manifest.json")
    return path


def check_flags(lines):
    return any(
        line.lstrip().startswith("[DEBUG] -d ")
        and all(flag in line for flag in (
            "-Xplugin:ErrorProne", "-Xep:NullAway:ERROR",
            "NullAway:JSpecifyMode=true", "-Werror", "nullaway-0.14.1.jar",
        ))
        for line in lines
    )


def main():
    checkpoint, = PLANS.glob("3396_*")
    start = read(checkpoint)
    scope = start["values"]
    core = scope["productionCoreMain"]
    source = scope["source"]
    assert git("rev-parse", "HEAD").decode().strip() == source
    previous_path = manifest("PG38856")
    current_path = manifest("PG43118")
    previous, current = read(previous_path), read(current_path)
    assert previous["stages"]["nullaway-compile"]["actualExit"] == 0
    assert current["productCore"] == core and current["results"]["passed"] == 14
    assert current["stageExits"]["compile"]["exit"] == 0
    assert all(pin(Path(x["path"])) == x for x in current["input"])
    root_pom = git("show", f"{core}:pom.xml")
    assert root_pom == git("show", f"{source}:pom.xml") == (ROOT / "pom.xml").read_bytes()
    pins = {Path(name): expected for name, expected in previous["inputHashes"].items()
            if "/src/main/java/" in name and name.endswith(".java")}
    assert len(pins) == 5 and {p.name for p in pins} == MAIN_FILES

    yaml, = (Path(x["path"]) for x in current["classpath"]
             if Path(x["path"]).name == "snakeyaml-engine-3.1.1.jar")
    assert pin(yaml) in current["classpath"]
    project_pom = BASE["HARNESS_POM"].replace("pgpt-outbox-nullaway-scope", "pgpt-config-nullaway-scope")
    project_pom = project_pom.replace(
        "  </dependencies>",
        "    <dependency><groupId>org.snakeyaml</groupId><artifactId>snakeyaml-engine</artifactId>"
        f"<version>3.1.1</version><scope>system</scope><systemPath>{yaml}</systemPath></dependency>\n"
        "  </dependencies>",
    )
    out = OPS / scope["run"]
    out.mkdir()
    raw = ROOT.parent / "pgpt-runs/PG379" / scope["run"]
    raw.mkdir(mode=0o700)
    maven, jdk = BASE["MAVEN"], BASE["JDK"]
    started = now()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-config-nullaway-") as name:
        work = Path(name)
        project, home = work / "scope", work / "home"
        home.mkdir()
        (work / "pom.xml").write_bytes(root_pom)
        payloads = []
        for path, expected in sorted(pins.items()):
            body = git("show", f"{core}:{path}")
            assert sha256(body).hexdigest() == expected
            assert body == path.read_bytes() == git("show", f"{source}:{path}")
            target = project / "src/main/java" / path.as_posix().split("/src/main/java/", 1)[1]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            payloads.append(pin(path))
        isolated_pom = project / "pom.xml"
        isolated_pom.write_text(project_pom)
        command = [str(maven), "-o", "-B", "-ntp", "-N", "-X", "-f", str(isolated_pom),
                   f"-Dmaven.repo.local={BASE['TOOLS'] / 'm2/repository'}", "-Dmaven.test.skip=true", "compile"]
        result = subprocess.run(command, cwd=project, capture_output=True, timeout=85, check=False,
                                env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": str(home),
                                     "JAVA_HOME": str(jdk), "MAVEN_SKIP_RC": "true",
                                     "MAVEN_OPTS": f"-Duser.home={home} -Djava.io.tmpdir={work}"})
        (raw / "compile.stdout").write_bytes(result.stdout)
        (raw / "compile.stderr").write_bytes(result.stderr)
        lines = result.stdout.decode("utf-8", errors="replace").splitlines()
        tree = project / "target/classes"
        built = {p.relative_to(tree).as_posix(): pin(p)["sha256"] for p in tree.rglob("*.class")}
        old = previous["physicalClassHashes"]
        controls = {
            "effectiveStrictNullAway": check_flags(lines),
            "exactFiveMainInputs": any("Compiling 5 source files" in line for line in lines),
            "exactQualifiedPhysicalNames": set(built) == set(old),
            "mavenSuccess": result.returncode == 0 and any("BUILD SUCCESS" in line for line in lines),
        }
        terminal = now()
    okay = all(controls.values())
    state = dict(run=scope["run"], source=source, productCore=core, startedAtUTC=started,
                 terminalAtUTC=terminal, actualExit=0 if okay else 1, mavenExit=result.returncode,
                 wbs="WBS-F03/2-2-b", startEvent=start["eventId"], command=command, controls=controls,
                 rootPomSha256=sha256(root_pom).hexdigest(), harnessPomSha256=sha256(project_pom.encode()).hexdigest(),
                 sources=payloads, dependency=pin(yaml), maven=pin(maven), javaCompiler=pin(jdk / "bin/javac"),
                 outputPhysical=[dict(className=k, sha256=v) for k, v in sorted(built.items())],
                 identicalPreviousPhysical=sum(built.get(k) == h for k, h in old.items()),
                 compileReceipts=[pin(raw / "compile.stdout"), pin(raw / "compile.stderr")],
                 previousMainScope=pin(previous_path), reusedUnchangedStrictFixtureCompileAndOrdinary=pin(current_path),
                 wholeF03=False, whole451=False, externalOperations=0, testsExecuted=0, formalAcceptanceId=None)
    with (out / "manifest.json").open("x") as handle:
        handle.write(json.dumps(state, indent=2) + "\n")
    print(controls, result.returncode, len(built), state["identicalPreviousPhysical"])
    return state["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
