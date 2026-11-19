"""Compile the four permitted modules and run the isolated lookup-reader fixture."""

from datetime import datetime, timezone
import gzip
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import tarfile
from tempfile import TemporaryDirectory


OPS = Path("evidence/01_PT/018_NK-OPS-001")
EVIDENCE = OPS / "evidence"
PLAN = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
COMMON = runpy.run_path(str(OPS / "input/5267_f02_controller_archunit_canaries.py"))
MODULES = ("protocol", "storage", "bootstrap", "batch")
CLASS = "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest"
METHODS = ("canonicalByteBoundaries", "malformedAndNull", "ownedCommandAndExit",
           "timeoutInterruptAndTermination", "stdioFailureMatrix", "sourceBufferAndNoLeak",
           "concurrentLookup", "gid009PreservesFatalReaderFailureThroughTheJdbcEdge")


def read(path):
    return json.loads(Path(path).read_bytes())


def run(out, label, command, cwd, env):
    begin = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=False, timeout=150)
    files = {}
    for prefix, data in (("stdout", result.stdout), ("stderr", result.stderr)):
        log = out / (label + "." + prefix + ".log.gz")
        log.write_bytes(gzip.compress(data, mtime=0))
        files[prefix] = COMMON["pin"](log)
    return dict(actualExit=result.returncode, command=[str(part) for part in command],
                beginUTC=begin, terminalAtUTC=datetime.now(timezone.utc).isoformat(), **files)


def main():
    start = read(next(PLAN.glob("767_*")))
    job = start["values"]
    git, pin = (COMMON[key] for key in ("git", "pin"))
    source, core = git("rev-parse", "HEAD").decode().strip(), git("rev-parse", "HEAD^").decode().strip()
    fixture, target = [item["path"] for item in job["oracleReferences"][-2:]]
    for meta in job["oracleReferences"]:
        path = meta["path"]
        if path in (fixture, target):
            assert COMMON["sha"](git("show", f"{job['source']}:{path}")) == meta["sha256"]
        else:
            assert pin(Path(path)) == meta
    assert git("diff", "--name-only", job["productionCoreMain"], core, "--",
               "src", ":(exclude)src/**/src/test/**").decode().splitlines() == [target]
    assert not git("diff", "--name-only", core, source, "--",
                   "src", ":(exclude)src/**/src/test/**")
    before = git("show", f"{job['source']}:{target}")
    after = git("show", f"{core}:{target}")
    assert after.replace(b"api.bootstrap.JdbcFailureGraph", b"storage.StorageIoException").replace(
        b"JdbcFailureGraph.preserveFatal", b"StorageIoException.preserveFatal") == before

    maven_reference = read(next(EVIDENCE.glob("PG39862-*/manifest.json")))
    old_unit = read(next(EVIDENCE.glob("PG40128-*/begin.json")))
    rules = read(next(EVIDENCE.glob("PG40210-*/begin.json")))
    java = Path(old_unit["jdk"]["path"])
    assert pin(java) == old_unit["jdk"] and all(pin(Path(row["path"])) == row for row in rules["toolAndRulePins"])
    maven = maven_reference["maven"]["command"]
    assert pin(Path(maven[0]))["sha256"] == maven_reference["tools"]["mavenLauncherSha256"]

    def tool(name):
        entry = old_unit["tools"][name]
        assert pin(Path(entry["path"])) == entry
        return Path(entry["path"])

    junit = tool("junit-platform-console-standalone-1.13.4.jar")
    agent = tool("org.jacoco.agent-0.8.15-runtime.jar")
    coverage_cli = tool("org.jacoco.cli-0.8.15-nodeps.jar")
    annotations = tool("jspecify-1.0.1.jar")
    out = (EVIDENCE / job["run"]).resolve()
    out.mkdir()
    selected = [f"--select-method={CLASS}#{method}" for method in METHODS]
    paths = ["pom.xml", "program/characterization/pom.xml", "src/schubert-nk-api/pom.xml",
             "src/schubert-nk-web/pom.xml", *(f"src/schubert-nk-{module}" for module in MODULES)]
    stages = {}
    facts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-group-lookup-") as temp:
        work = Path(temp)
        snapshot = git("archive", source, *paths)
        with tarfile.open(fileobj=io.BytesIO(snapshot)) as archive:
            archive.extractall(work, filter="data")
        env = {"JAVA_HOME": str(java.parents[1]), "PATH": str(java.parent) + ":/usr/bin:/bin",
               "LANG": "C.UTF-8", "USER": "mini"}
        modules = {name: work / f"src/schubert-nk-{name}/target/classes" for name in MODULES}
        cp = os.pathsep.join(map(str, (*modules.values(), junit, annotations)))
        execution = out / "jacoco.exec"
        xml = out / "xml"
        xml.mkdir()
        init = work / "class-init.log"
        sources = work / "static-sources.txt"
        sources.write_text(str(work / target) + "\n" + str(work / fixture) + "\n")
        checkstyle = rules["commands"]["checkstyle"][:]
        checkstyle[checkstyle.index("-o") + 1] = out / "checkstyle.xml"
        checkstyle[-1] = "@" + str(sources)
        production = CLASS.removesuffix("Test")
        old_jar = read(job["oracleReferences"][1]["path"])["jars"]["batch"]["artifact"]
        assert pin(Path(old_jar["path"])) == old_jar
        javap = java.with_name("javap")
        commands = {
            "compile": maven,
            "format": [*rules["commands"]["format"][:6], work / target, work / fixture],
            "checkstyle": checkstyle,
            "abi-before": [javap, "-classpath", old_jar["path"], "-p", "-s", production],
            "abi-after": [javap, "-classpath", modules["batch"], "-p", "-s", production],
            "behavior-after": [javap, "-classpath", modules["batch"], "-p", "-c", production],
            "testcompile": [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror",
                            "-proc:none", "-cp", cp, "-d", work / "selected-test", work / fixture],
            "unit": [java, "-Xmx256m", f"-Xlog:class+init=info:file={init}",
                     f"-javaagent:{agent}=destfile={execution},sessionid=PG40308-GID,append=false",
                     "-jar", junit, "execute", "--disable-banner", "--details=summary", "--fail-if-no-tests",
                     "--class-path", str(work / "selected-test") + os.pathsep + cp,
                     "--reports-dir", xml, *selected],
            "coverage": [java, "-jar", coverage_cli, "report", execution, "--classfiles", modules["batch"],
                         "--xml", out / "coverage.xml"],
        }
        for label, command in commands.items():
            stages[label] = run(out, label, command, work, env)
            if stages[label]["actualExit"] != 0:
                break
        if "abi-after" in stages and stages["abi-after"]["actualExit"] == 0:
            old_abi, new_abi = (gzip.decompress(Path(stages[label]["stdout"]["path"]).read_bytes())
                                for label in ("abi-before", "abi-after"))
            assert old_abi == new_abi and pin(Path(old_jar["path"])) == old_jar
        if init.is_file():
            (out / "class-init.log.gz").write_bytes(gzip.compress(init.read_bytes(), mtime=0))
        if stages["compile"]["actualExit"] == 0:
            produced = {name: {str(p.relative_to(folder)): pin(p)["sha256"]
                               for p in sorted(folder.rglob("*.class"))}
                        for name, folder in modules.items()}
            prior = maven_reference["physicalClassHashes"]
            delta = {name: sorted(entry for entry in current.keys() | prior[name].keys()
                                  if current.get(entry) != prior[name].get(entry))
                     for name, current in produced.items()}
            facts = dict(modules={name: len(rows) for name, rows in produced.items()},
                         physicalDelta=delta, classHashes=produced)
            with (out / "compiled-classes.json").open("x") as stream:
                json.dump(facts, stream, indent=2)
    result = dict(source=source, productionCore=core, productionPrevious=job["productionCoreMain"],
                  testFixture=fixture, productionTarget=target, stages=stages, frozenCommandFiles=paths,
                  selectedTests=list(METHODS), notRun=["nativeFactory"], namedActualHostActions=0,
                  compiled=pin(out / "compiled-classes.json") if facts else None,
                  actualExit=next((stage["actualExit"] for stage in stages.values()
                                   if stage["actualExit"] != 0), 0),
                  wholeF02Accepted=False, whole451Accepted=False, terminalAtUTC=COMMON["timestamp"]())
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), result["actualExit"])
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
