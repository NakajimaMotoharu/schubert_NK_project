"""Compile the four permitted modules and run one explicitly selected upper-boundary fixture."""

from datetime import datetime, timezone
import gzip
import io
import json
import os
from pathlib import Path
import re
import shutil
import runpy
import subprocess
import sys
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
RELEASE_CLASS = "dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest"
BROKER_CLASS = "dev.codex.schubert.nk.batch.mq.ArtemisStartupObservationTest"
PROFILES = {
    "lookup": ("767_*", CLASS, "batch", "PG40308-GID"),
    "public-rfc": ("770_*", RELEASE_CLASS, "bootstrap", "PG40314-PUBLIC-RFC"),
    "borrowed-broker": ("773_*", BROKER_CLASS, "batch", "PG40320-BORROWED"),
    "borrowed-catalog": ("788_*", "", "batch", "PG40338-CATALOG"),
    "borrowed-settings": ("791_*", "", "batch", "PG40344-SETTINGS"),
    "borrowed-expiry": ("794_*", "", "batch", "PG40350-EXPIRY"),
    "public-checkpoint": ("812_*", "", "bootstrap", "PG40374-PUBLIC-CHECKPOINT"),
}


def read(path):
    return json.loads(Path(path).read_bytes())


def broker_dependencies(plan, local_repo):
    manifest = Path(plan["oracleReferences"][3]["path"])
    assert COMMON["pin"](manifest) == plan["oracleReferences"][3]
    tree = read(manifest.with_name("batch-tree.json"))
    names = {"artemis-core-client", "artemis-commons", "netty-buffer", "netty-common", "slf4j-api"}
    resolved = {}
    pending = [tree]
    while pending:
        node = pending.pop()
        name = node["artifactId"]
        if name in names and node["scope"] in ("compile", "runtime") and node["type"] == "jar":
            version = node["version"]
            path = local_repo.joinpath(*node["groupId"].split("."), name, version, f"{name}-{version}.jar")
            assert name not in resolved or resolved[name] == path
            resolved[name] = path
        pending.extend(node.get("children", []))
    assert set(resolved) == names
    assert all(path.is_file() and path.resolve() == path for path in resolved.values())
    return [resolved[key] for key in sorted(resolved)]


def checkpoint_dependencies(job):
    prepare = read(job["oracleReferences"][3]["path"])
    original = Path(prepare["work"]) / "test-classes"
    name = "dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpointTest"
    source = f"src/schubert-nk-bootstrap/src/test/java/{name}.java"
    assert prepare["testSourceHashes"][source] == COMMON["sha"](
        COMMON["git"]("show", f"{job['source']}:{source}"))
    files = {}
    for suffix in ("", "$PublicFixture", "$PublicRtFixture"):
        part = f"{name}{suffix}.class"
        path = original / part
        assert path.resolve() == path
        expected = prepare["testPhysicalHashes"][part]
        assert COMMON["pin"](path)["sha256"] == expected
        files[part] = path
    annotation, = [Path(path) for path in prepare["toolDependencyHashes"]
                  if Path(path).name == "spotbugs-annotations-4.10.4.jar"]
    assert COMMON["pin"](annotation)["sha256"] == prepare["toolDependencyHashes"][str(annotation)]
    return files, annotation


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


def main(profile="lookup"):
    pattern, test_class, output_module, session = PROFILES[profile]
    lookup = profile == "lookup"
    start = read(next(PLAN.glob(pattern)))
    job = start["values"]
    git, pin = (COMMON[key] for key in ("git", "pin"))
    source = git("rev-parse", "HEAD").decode().strip()
    catalog = "tests" in job
    core = source if profile == "public-rfc" or catalog else git("rev-parse", "HEAD^").decode().strip()
    fixtures = job["tests"] if catalog else [job["oracleReferences"][-2]["path"]]
    targets = job["targets"] if catalog else [job["oracleReferences"][-1]["path"]]
    for meta in job["oracleReferences"]:
        path = meta["path"]
        if path in [*fixtures, *targets] or path.endswith("/038_NK-OPS-001_Artemis起動前観測単体テスト仕様書.md"):
            assert COMMON["sha"](git("show", f"{job['source']}:{path}")) == meta["sha256"]
        else:
            assert pin(Path(path)) == meta
    assert sorted(git("diff", "--name-only", job["productionCoreMain"], core, "--",
                      "src", ":(exclude)src/**/src/test/**").decode().splitlines()) == sorted(targets)
    assert not git("diff", "--name-only", core, source, "--",
                   "src", ":(exclude)src/**/src/test/**")
    for target in targets:
        before = git("show", f"{job['source']}:{target}")
        after = git("show", f"{core}:{target}")
        restored = after.replace(b"api.bootstrap.JdbcFailureGraph", b"storage.StorageIoException").replace(
            b"JdbcFailureGraph.preserveFatal", b"StorageIoException.preserveFatal")
        restored = re.sub(rb"(?:^import [^\n]+\n)+",
                          lambda match: b"".join(sorted(match[0].splitlines(keepends=True))),
                          restored, flags=re.MULTILINE)
        assert restored == before

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
    dependencies = []
    if profile.startswith("borrowed-"):
        repo = Path(next(part.split("=", 1)[1] for part in maven if part.startswith("-Dmaven.repo.local=")))
        dependencies = broker_dependencies(job, repo)
    companion = {}
    if profile == "public-checkpoint":
        companion, annotation = checkpoint_dependencies(job)
        dependencies = [annotation]
    pins = [pin(path) for path in dependencies]
    companion_pins = {part: pin(path) for part, path in companion.items()}
    out = (EVIDENCE / job["run"]).resolve()
    out.mkdir()
    selected_classes = [path.split("/src/test/java/")[1].removesuffix(".java").replace("/", ".")
                        for path in fixtures]
    selected = ([f"--select-method={test_class}#{method}" for method in METHODS] if lookup
                else [f"--select-class={name}" for name in selected_classes])
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
        selected_output = work / "selected-test"
        for part, path in companion.items():
            output = selected_output / part
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, output)
            assert pin(output)["sha256"] == companion_pins[part]["sha256"]
        cp_entries = [*modules.values(), junit, annotations, *dependencies]
        if companion:
            cp_entries.append(selected_output)
        cp = os.pathsep.join(map(str, cp_entries))
        execution = out / "jacoco.exec"
        xml = out / "xml"
        xml.mkdir()
        init = work / "class-init.log"
        sources = work / "static-sources.txt"
        source_paths = [work / path for path in [*targets, *fixtures]]
        sources.write_text("".join(str(path) + "\n" for path in source_paths))
        checkstyle = rules["commands"]["checkstyle"][:]
        checkstyle[checkstyle.index("-o") + 1] = out / "checkstyle.xml"
        checkstyle[-1] = "@" + str(sources)
        production = [path.split("/src/main/java/")[1].removesuffix(".java").replace("/", ".")
                      for path in targets]
        analysis_types = job.get("analysisTypes", production)
        old_jar = read(job["oracleReferences"][1]["path"])["jars"][output_module]["artifact"]
        assert pin(Path(old_jar["path"])) == old_jar
        javap = java.with_name("javap")
        commands = {
            "compile": maven,
            "format": [*rules["commands"]["format"][:6], *source_paths],
            "checkstyle": checkstyle,
            "abi-before": [javap, "-classpath", old_jar["path"], "-p", "-s", *analysis_types],
            "abi-after": [javap, "-classpath", modules[output_module], "-p", "-s", *analysis_types],
            "behavior-after": [javap, "-classpath", modules[output_module], "-p", "-c", *analysis_types],
            "testcompile": [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror",
                            "-proc:none", "-cp", cp, "-d", selected_output,
                            *(work / path for path in fixtures)],
            "unit": [java, "-Xmx256m", f"-Xlog:class+init=info:file={init}",
                     f"-javaagent:{agent}=destfile={execution},sessionid={session},append=false",
                     "-jar", junit, "execute", "--disable-banner", "--details=summary", "--fail-if-no-tests",
                     "--class-path", cp if companion else str(selected_output) + os.pathsep + cp,
                     "--reports-dir", xml, *selected],
            "coverage": [java, "-jar", coverage_cli, "report", execution, "--classfiles", modules[output_module],
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
            prior = maven_reference["physicalClassHashes"] if lookup else read(job["oracleReferences"][2]["path"])["classHashes"]
            delta = {name: sorted(entry for entry in current.keys() | prior[name].keys()
                                  if current.get(entry) != prior[name].get(entry))
                     for name, current in produced.items()}
            facts = dict(modules={name: len(rows) for name, rows in produced.items()},
                         physicalDelta=delta, classHashes=produced)
            if not lookup:
                crc = runpy.run_path(str(OPS / "input/5257_p01810_broker_evidence_value_post.py"))["crc64"]
                names = [name.replace(".", "/") for name in production]
                exact = [item for item in produced[output_module]
                         if any(item == name + ".class" or item.startswith(name + "$") for name in names)]
                facts["selectedPhysicalCrc"] = {
                    item.removesuffix(".class"): crc((modules[output_module] / item).read_bytes())
                    for item in exact
                }
            with (out / "compiled-classes.json").open("x") as stream:
                json.dump(facts, stream, indent=2)
    result = dict(source=source, productionCore=core, productionPrevious=job["productionCoreMain"],
                  testFixture=fixtures if catalog else fixtures[0],
                  productionTarget=targets if catalog else targets[0],
                  stages=stages, frozenCommandFiles=paths,
                  selectedTests=list(METHODS) if lookup else selected,
                  notRun=["nativeFactory"] if lookup else [], namedActualHostActions=0,
                  session=session,
                  extraDependencies=pins, companionClasses=companion_pins,
                  compiled=pin(out / "compiled-classes.json") if facts else None,
                  actualExit=next((stage["actualExit"] for stage in stages.values()
                                   if stage["actualExit"] != 0), 0),
                  wholeF02Accepted=False, whole451Accepted=False, terminalAtUTC=COMMON["timestamp"]())
    assert [pin(path) for path in dependencies] == pins
    assert {part: pin(path) for part, path in companion.items()} == companion_pins
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), result["actualExit"])
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
