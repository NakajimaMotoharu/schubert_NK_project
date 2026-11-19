"""Package the current permitted outputs and verify the narrow dependency delta."""

from collections import defaultdict
from datetime import datetime, timezone
import gzip
import io
from pathlib import Path
import re
import runpy
import shutil
import stat
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile


INPUT = Path(__file__).parent
UPPER = runpy.run_path(str(INPUT / "5326_f02_group_lookup_upper.py"))
PACKAGE = runpy.run_path(str(INPUT / "5251_f02_current_four_jars.py"))
OPS, PLAN, COMMON = (UPPER[k] for k in ("EVIDENCE", "PLAN", "COMMON"))
MODULES = UPPER["MODULES"]
EDGE = re.compile(rb"^\s+(dev\.codex\.schubert\.nk\.\S+)\s+->\s+(\S+)", re.MULTILINE)


def dependency_rows(receipt):
    data = gzip.decompress(Path(receipt["stdout"]["path"]).read_bytes())
    result = defaultdict(set)
    for source, destination in EDGE.findall(data):
        result[source.decode()].add(destination.decode())
    return result


def main():
    read = UPPER["read"]
    start = read(next(PLAN.glob("776_*")))
    job = start["values"]
    git, pin, dump = (COMMON[name] for name in ("git", "pin", "dump"))
    assert git("rev-parse", "HEAD").decode().strip() == job["source"]
    assert all(pin(Path(meta["path"])) == meta for meta in job["oracleReferences"])
    previous = read(job["oracleReferences"][1]["path"])
    compiled = read(job["oracleReferences"][2]["path"])
    source = job["productionCoreMain"]
    assert not git("diff", "--name-only", source, job["source"], "--", "pom.xml",
                   "src", ":(exclude)src/**/src/test/**")
    assert previous["sourceCore"] != source
    base = read(job["oracleReferences"][-1]["path"])
    maven = base["maven"]["command"]
    checkout_paths = ["pom.xml", "program/characterization/pom.xml",
                      "src/schubert-nk-api/pom.xml", "src/schubert-nk-web/pom.xml",
                      *(f"src/schubert-nk-{module}" for module in MODULES)]
    local = Path(next(part.split("=", 1)[1] for part in maven if part.startswith("-Dmaven.repo.local=")))
    plugin = local / "org/apache/maven/plugins/maven-jar-plugin/3.4.1/maven-jar-plugin-3.4.1.jar"
    old_plugin = previous["mavenPlugin"]
    assert pin(plugin) == old_plugin
    java = next(UPPER["EVIDENCE"].glob("PG40128-*/begin.json"))
    runtime = Path(read(java)["jdk"]["path"])
    assert pin(runtime)["sha256"] == base["tools"]["javaSha256"]
    assert pin(Path(maven[0]))["sha256"] == base["tools"]["mavenLauncherSha256"]
    env = {"JAVA_HOME": str(runtime.parents[1]), "PATH": str(runtime.parent) + ":/usr/bin:/bin",
           "LANG": "C.UTF-8", "USER": "mini"}
    out = (OPS / job["run"]).resolve()
    out.mkdir()
    preserved = Path.cwd().parent / "pgpt-runs/PG379" / job["run"].lower()
    preserved.mkdir(mode=0o700)
    jar_run = maven[:-2] + ["org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar"]
    stages, packaged = {}, {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-four-jars-") as temp:
        work = Path(temp)
        snapshot = git("archive", source, *checkout_paths)
        with tarfile.open(fileobj=io.BytesIO(snapshot)) as archive:
            archive.extractall(work, filter="data")
        stages["compile"] = UPPER["run"](out, "compile", maven, work, env)
        assert stages["compile"]["actualExit"] == 0
        folders = {name: work / f"src/schubert-nk-{name}" for name in MODULES}
        wanted = compiled["classHashes"]
        current = {name: PACKAGE["inventory"](folder / "target/classes") for name, folder in folders.items()}
        assert current == wanted and sum(map(len, current.values())) == 1102
        stages["jar"] = UPPER["run"](out, "jar", jar_run, work, env)
        assert stages["jar"]["actualExit"] == 0
        jar_log = gzip.decompress(Path(stages["jar"]["stdout"]["path"]).read_bytes())
        assert jar_log.count(b"Building jar:") == 4 and b"BUILD SUCCESS" in jar_log
        differences = {}
        subsequent = {"batch": ["ConfigurationGroupResolver.class", "ArtemisStartupObservation.class"],
                      "bootstrap": ["ReleaseSignatureVerifier.class"]}
        for name, folder in folders.items():
            artifact_name = folder.name
            archive = folder / f"target/{artifact_name}-0.1.0-SNAPSHOT.jar"
            dest = preserved / archive.name
            shutil.copyfile(archive, dest)
            dest.chmod(0o600)
            packaged[name] = PACKAGE["verify_jar"](dest, artifact_name, wanted[name],
                                                  (folder / "pom.xml").read_bytes())
            prior_pin = previous["jars"][name]["artifact"]
            prior = Path(prior_pin["path"])
            assert stat.S_ISREG(prior.lstat().st_mode) and prior.resolve() == prior and pin(prior) == prior_pin
            with ZipFile(prior) as old:
                old_class = {item: COMMON["sha"](old.read(item)) for item in old.namelist()
                             if item.endswith(".class")}
                assert old_class.keys() == wanted[name].keys()
                changed = sorted(item for item in old_class if old_class[item] != wanted[name][item])
                assert sorted(Path(item).name for item in changed) == sorted(subsequent.get(name, []))
                differences[name] = changed
                for item in changed:
                    dest = work / "old" / item
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(old.read(item))
        common = [runtime.with_name("jdeps"), "-verbose:class", "-filter:none", "--ignore-missing-deps"]
        old_inputs, new_inputs = [], []
        for name in MODULES:
            for item in differences[name]:
                old_inputs.append(work / "old" / item)
                new_inputs.append(folders[name] / "target/classes" / item)
        for kind, inputs in (("edges-before", old_inputs), ("edges-after", new_inputs)):
            stages[kind] = UPPER["run"](out, kind, [*common, *inputs], work, env)
            assert stages[kind]["actualExit"] == 0
        before, after = (dependency_rows(stages[k]) for k in ("edges-before", "edges-after"))
        assert before.keys() == after.keys() and len(after) == 3
        jdbc = "dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph"
        storage = "dev.codex.schubert.nk.storage.StorageIoException"
        assert all(after[k] - before[k] == {jdbc} and before[k] - after[k] == {storage}
                   for k in after)
        edges = {k: dict(added=[jdbc], removed=[storage], identicalCount=len(after[k] & before[k]))
                 for k in sorted(after)}
    dump(out / "manifest.json", dict(
        actualExit=0, run=job["run"], startEvent=start["eventId"], sourceCore=source,
        gitHead=job["source"], inputClassCount=1102, sourceMain=base["mainCounts"],
        jars=packaged, changedClassesFromOldJars=differences, exactMatchedCurrentCompiledClassCount=1102,
        exactNewTypedEdges=edges, mavenPlugin=old_plugin, execution=stages["jar"], stages=stages,
        priorBuildOnly=job["oracleReferences"][2], originalPackagedJars=job["oracleReferences"][1],
        testsExecuted=0, actualHostActions=0, wholeF02Accepted=False, whole451Accepted=False,
        untestedModules=["api", "web"], terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
