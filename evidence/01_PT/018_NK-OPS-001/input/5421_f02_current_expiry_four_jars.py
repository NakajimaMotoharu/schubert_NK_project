"""Build the four authorized Main modules at the ExpiryAudit candidate."""

import io
from pathlib import Path
import runpy
import shutil
import sys
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile


PRECEDENT = runpy.run_path(str(Path(__file__).with_name("5364_f02_utc42_four_current_jars.py")))
OPS, PLAN, COMMON, PACKAGE, MODULES, UPPER = (
    PRECEDENT[name] for name in ("OPS", "PLAN", "COMMON", "PACKAGE", "MODULES", "UPPER")
)
TARGET = "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.class"


def main(mode):
    final_ownership = mode == "final-ownership"
    terminal_success = mode == "terminal-success"
    target_type = TARGET.replace("ExpiryAuditRepository", "CleanupTerminalRepository") if terminal_success else TARGET
    read = UPPER["read"]
    pin, sha, git, write = (COMMON[key] for key in ("pin", "sha", "git", "dump"))
    start_doc = "1098_F02*" if terminal_success else "1089_F02*" if final_ownership else "1065_F02*"
    group = read(next(PLAN.glob(start_doc)))
    task = group["values"]
    assert all(pin(Path(item["path"])) == item for item in task["oracleReferences"])
    previous, selected, prior, tools = (read(row["path"]) for row in task["oracleReferences"][1:])
    checkpoint = read(Path(task["oracleReferences"][0]["path"]))
    qualified = task["productionCoreMain"]
    if terminal_success:
        candidate = checkpoint["candidateProductionSource"]
        old_core = previous["candidateProductionSource"]
        assert old_core == selected["beforeProduct"] and qualified == previous["lastQualifiedCore"]
        baseline_jars = previous["privateJars"]
    else:
        candidate = checkpoint["candidateProductionSource"] if final_ownership else prior["candidateProductionSource"]
        old_core = previous["productionCore"]
        assert qualified == old_core == prior["lastQualifiedCore"]
        baseline_jars = previous["packagedBuild"]
    selected_main = selected["candidateMain"] if final_ownership or terminal_success else selected["candidateSource"]
    changed = git("diff", "--name-only", old_core, candidate, "--", "src", "pom.xml",
                  ":(exclude)src/**/src/test/**").decode().splitlines()
    assert changed == [selected_main["path"]]
    assert sha(git("show", f"{candidate}:{changed[0]}")) == selected_main["sha256"]
    assert git("rev-parse", "HEAD").decode().strip() == task["source"]
    assert not git("diff", "--name-only", candidate, task["source"], "--", "pom.xml", "src")
    java = Path(read(next(OPS.glob("PG40128-*/begin.json")))["jdk"]["path"])
    build = tools["maven"]["command"]
    assert pin(Path(build[0]))["sha256"] == tools["tools"]["mavenLauncherSha256"]
    assert pin(java)["sha256"] == tools["tools"]["javaSha256"]
    assert build[-2:] == ["-am", "compile"] and "-o" in build
    package = [*build[:-2], "org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar"]
    modules = {name: Path("src") / f"schubert-nk-{name}" for name in MODULES}
    archive_tree = ["pom.xml", "program/characterization/pom.xml",
                    "src/schubert-nk-api/pom.xml", "src/schubert-nk-web/pom.xml"]
    archive_tree += [str(path / leaf) for path in modules.values() for leaf in ("pom.xml", "src/main")]
    roster_paths = git("ls-tree", "-r", "--name-only", candidate, *archive_tree).decode().splitlines()
    forbidden_bases = {"TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec",
                       "WebStartupException", "RootFailedStartRecoveryTest", "RootFailedStartPairRecoveryTest"}
    assert len([p for p in roster_paths if p.endswith(".java")]) == 482
    assert not any("/src/test/" in path or Path(path).stem in forbidden_bases for path in roster_paths)
    assert set(modules) == {"protocol", "storage", "bootstrap", "batch"}
    assert shutil.disk_usage("/dev/shm").free > 512 * 1024**2

    run = task["run"]
    out = (OPS / run).resolve()
    private = (Path.cwd().parent / "pgpt-runs/PG379" / run.lower()).resolve()
    out.mkdir()
    verify, stages, deltas, artifacts = {}, {}, {}, {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-current-expiry-four-") as temporary:
        root = Path(temporary)
        home = root / "maven-home"
        home.mkdir()
        env = {"JAVA_HOME": str(java.parents[1]), "PATH": str(java.parent) + ":/usr/bin:/bin",
               "LANG": "C.UTF-8", "HOME": str(home), "MAVEN_SKIP_RC": "true",
               "MAVEN_OPTS": f"-Duser.home={home} -Djava.io.tmpdir={root}"}
        with tarfile.open(fileobj=io.BytesIO(git("archive", candidate, *archive_tree))) as archive:
            archive.extractall(root, filter="data")
        write(out / "begin.json", dict(run=run, candidate=candidate, startEvent=group["eventId"],
                                      inputArchivePaths=archive_tree, javaFiles=482, command=build))
        stages["compile"] = UPPER["run"](out, "compile", build, root, env)
        if stages["compile"]["actualExit"] == 0:
            stages["package"] = UPPER["run"](out, "package", package, root, env)
        if stages.get("package", {}).get("actualExit") == 0:
            private.mkdir(mode=0o700)
            for name, path in modules.items():
                prior = baseline_jars[name]["artifact"]
                assert pin(Path(prior["path"])) == prior
                with ZipFile(prior["path"]) as current:
                    before = {f: sha(current.read(f)) for f in current.namelist() if f.endswith(".class")}
                    if name == "batch":
                        old_file = root / "before" / target_type
                        old_file.parent.mkdir(parents=True)
                        old_file.write_bytes(current.read(target_type))
                target_dir = root / path / "target/classes"
                after = PACKAGE["inventory"](target_dir)
                assert set(before) == set(after)
                deltas[name] = sorted(k for k in after if before[k] != after[k])
                jar = private / (path.name + "-0.1.0-SNAPSHOT.jar")
                shutil.copyfile(target_dir.parent / jar.name, jar)
                jar.chmod(0o600)
                artifacts[name] = PACKAGE["verify_jar"](jar, path.name, after, (root / path / "pom.xml").read_bytes())
            assert sum(item["classes"] for item in artifacts.values()) == 1102
            changed_types = {item for paths in deltas.values() for item in paths}
            if terminal_success:
                assert target_type in changed_types and all(name.startswith(target_type[:-6]) for name in changed_types)
            else:
                assert changed_types == {target_type}
            batch_classes = root / modules["batch"] / "target/classes"
            new_file = batch_classes / target_type
            focused_glob = "PG40730-*/manifest.json" if final_ownership else "PG40696-*-after/manifest.json"
            if terminal_success:
                focused_glob = "PG40740-*-after/manifest.json"
            focused = read(next(OPS.glob(focused_glob)))
            verify["focusedPhysicalByteEqual"] = all(
                sha((batch_classes/name).read_bytes()) == fingerprint for name, fingerprint in focused["physical"].items()
            )
            if terminal_success:
                expiry = read(next(OPS.glob("PG40730-*/manifest.json")))["physical"]
                verify["retainedExpiryPhysicalByteEqual"] = all(
                    sha((batch_classes/name).read_bytes()) == fingerprint for name, fingerprint in expiry.items()
                )
            for mode, file in (("before", old_file), ("after", new_file)):
                stages[f"jdeps-{mode}"] = UPPER["run"](
                    out, f"jdeps-{mode}", [java.with_name("jdeps"), "-verbose:class", "-filter:none",
                                           "--ignore-missing-deps", file], root, env)
                stages[f"abi-{mode}"] = UPPER["run"](
                    out, f"abi-{mode}", [java.with_name("javap"), "-public", "-s", file], root, env)
            before_edges, after_edges = (
                PRECEDENT["G"]["dependency_rows"](stages[f"jdeps-{mode}"]) for mode in ("before", "after")
            )
            origin = target_type.removesuffix(".class").replace("/", ".")
            assert before_edges.keys() == after_edges.keys() == {origin}
            verify["removedEdges"] = sorted(before_edges[origin] - after_edges[origin])
            verify["addedEdges"] = sorted(after_edges[origin] - before_edges[origin])
            verify["publicAbiEqual"] = (
                stages["abi-before"]["stdout"]["sha256"] == stages["abi-after"]["stdout"]["sha256"]
            )
    removed = [] if terminal_success else ["dev.codex.schubert.nk.storage.StorageIoException"]
    result = (
        len(stages) == 6 and all(row["actualExit"] == 0 for row in stages.values())
        and verify.get("removedEdges") == removed
        and verify.get("addedEdges") == ["dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph"]
        and verify.get("publicAbiEqual") is True
    )
    receipt = dict(actualExit=0 if result else 1, gitHead=task["source"], candidateProductionSource=candidate,
                   lastQualifiedCore=qualified, comparisonBuildCore=old_core, startEvent=group["eventId"], commands=stages,
                   privateJars=artifacts, changedPhysical=deltas, verify=verify, mavenModules=list(MODULES),
                   sources=482, physical=sum(item["classes"] for item in artifacts.values()),
                   productTestsStarted=0, apiWebMainIncluded=False, operationalActions=0,
                   fullSixBuild=False, whole451=False, newFormalAcceptance=0, terminalAtUTC=COMMON["timestamp"]())
    write(out / "manifest.json", receipt)
    print(dict(exits={key: row["actualExit"] for key, row in stages.items()},
               physical=receipt["physical"], verify=verify))
    return receipt["actualExit"]


if __name__ == "__main__":
    assert sys.argv[1:] in ([], ["final-ownership"], ["terminal-success"])
    raise SystemExit(main(sys.argv[1] if len(sys.argv) == 2 else "legacy-expiry"))
