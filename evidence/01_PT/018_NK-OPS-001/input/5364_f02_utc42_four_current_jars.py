"""Build and package the four previously admitted Main module inputs after SSC-473."""

import io
from pathlib import Path
import runpy
import shutil
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile


G = runpy.run_path(str(Path(__file__).with_name("5331_f02_current_jars_and_edges.py")))
OPS, PLAN, COMMON, PACKAGE, MODULES, UPPER = (
    G[k] for k in ("OPS", "PLAN", "COMMON", "PACKAGE", "MODULES", "UPPER"))
TARGETS = {"MigrationGamesVerifier.class", "MigrationMasterContentVerifier.class"}
REMOVED = "java.sql.Timestamp"
REPLACEMENT = "java.time.OffsetDateTime"


def main():
    read = UPPER["read"]
    git, pin, dump, timestamp = (COMMON[name] for name in ("git", "pin", "dump", "timestamp"))
    start = read(next(PLAN.glob("872_*")))
    w = start["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in w["oracleReferences"])
    old, physical, quality, toolchain = (read(ref["path"]) for ref in w["oracleReferences"][1:])
    core = w["productionCoreMain"]
    assert core == quality["source"] and quality["verifiedAttempt"] == {"pass": 87}
    assert not git("diff", "--name-only", core, w["source"], "--", "pom.xml", "src",
                   ":(exclude)src/**/src/test/**")
    names = git("diff", "--name-only", old["sourceCore"], core, "--", "pom.xml", "src",
                ":(exclude)src/**/src/test/**").decode().splitlines()
    assert {Path(n).with_suffix(".class").name for n in names} == TARGETS and len(names) == 2
    assert all("/schubert-nk-bootstrap/src/main/" in n for n in names)
    command = toolchain["maven"]["command"]
    maven = Path(command[0])
    java = Path(read(next(OPS.glob("PG40128-*/begin.json")))["jdk"]["path"])
    assert pin(java)["sha256"] == toolchain["tools"]["javaSha256"]
    assert pin(maven)["sha256"] == toolchain["tools"]["mavenLauncherSha256"]
    plug = old["mavenPlugin"]
    assert pin(Path(plug["path"])) == plug
    jar = command[:-2] + ["org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar"]
    modules = {key: Path(f"src/schubert-nk-{key}") for key in MODULES}
    tree = ["pom.xml", "program/characterization/pom.xml", "src/schubert-nk-api/pom.xml",
            "src/schubert-nk-web/pom.xml",
            *(str(path / suffix) for path in modules.values() for suffix in ("pom.xml", "src/main"))]
    files = git("ls-tree", "-r", "--name-only", core, *tree).decode().splitlines()
    assert all("/src/test/" not in f for f in files)
    assert all(Path(f).stem not in ("TemporaryInfrastructureException", "FingerprintKeyRing",
                                    "ResponseSnapshotCodec", "WebStartupException") for f in files)
    assert sum(f.endswith(".java") for f in files) == 482
    env = {"JAVA_HOME": str(java.parents[1]), "PATH": str(java.parent) + ":/usr/bin:/bin",
           "LANG": "C.UTF-8", "USER": "mini"}
    out = (OPS / w["run"]).resolve()
    out.mkdir()
    stages, packaged, all_hashes, differences, edges = {}, {}, {}, {}, {}
    baseline = physical["classHashes"]
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-utc42-four-") as folder:
        root = Path(folder)
        with tarfile.open(fileobj=io.BytesIO(git("archive", core, *tree))) as source:
            source.extractall(root, filter="data")
        stages["compile"] = UPPER["run"](out, "compile", command, root, env)
        if stages["compile"]["actualExit"] == 0:
            stages["jar"] = UPPER["run"](out, "jar", jar, root, env)
        if "jar" in stages and stages["jar"]["actualExit"] == 0:
            preserved = Path.cwd().parent / "pgpt-runs/PG379" / w["run"].lower()
            preserved.mkdir(mode=0o700)
            old_files, new_files = [], []
            for key, path in modules.items():
                folder = root / path
                classes = PACKAGE["inventory"](folder / "target/classes")
                assert classes.keys() == baseline[key].keys()
                delta = sorted(item for item, sha in classes.items() if baseline[key][item] != sha)
                expected = TARGETS if key == "bootstrap" else set()
                assert {Path(item).name for item in delta} == expected
                all_hashes[key] = classes
                differences[key] = delta
                original = old["jars"][key]["artifact"]
                original_path = Path(original["path"])
                assert pin(original_path) == original
                archive = folder / f"target/{path.name}-0.1.0-SNAPSHOT.jar"
                copy = preserved / archive.name
                shutil.copyfile(archive, copy)
                copy.chmod(0o600)
                packaged[key] = PACKAGE["verify_jar"](copy, path.name, classes, (folder / "pom.xml").read_bytes())
                with ZipFile(original_path) as prior:
                    for item in delta:
                        f = root / "prior" / item
                        f.parent.mkdir(parents=True, exist_ok=True)
                        data = prior.read(item)
                        assert COMMON["sha"](data) == baseline[key][item]
                        f.write_bytes(data)
                        old_files.append(f)
                        new_files.append(folder / "target/classes" / item)
            assert sum(map(len, all_hashes.values())) == 1102
            dep = [java.with_name("jdeps"), "-verbose:class", "-filter:none", "--ignore-missing-deps"]
            for label, classfiles in (("typed-before", old_files), ("typed-after", new_files)):
                stages[label] = UPPER["run"](out, label, [*dep, *classfiles], root, env)
                assert stages[label]["actualExit"] == 0
            prior, current = (G["dependency_rows"](stages[label]) for label in ("typed-before", "typed-after"))
            assert prior.keys() == current.keys() and len(current) == 2
            for name in sorted(current):
                added, removed = current[name] - prior[name], prior[name] - current[name]
                assert removed == {REMOVED} and REPLACEMENT in added and added <= {REPLACEMENT, "java.lang.Class"}
                edges[name] = dict(added=sorted(added), removed=sorted(removed),
                                   unchangedDependencies=len(current[name] & prior[name]))
    exit_code = next((v["actualExit"] for v in stages.values() if v["actualExit"] != 0), 0)
    proof = dict(actualExit=exit_code, sourceCore=core, gitHead=w["source"], baselineCore=old["sourceCore"],
                 started=start["eventId"], sourceCounts=toolchain["mainCounts"], statuses=stages,
                 oldJarManifest=w["oracleReferences"][1], oldPhysicalManifest=w["oracleReferences"][2],
                 packagedJars=packaged, changedPhysical=differences, exactTypedChanges=edges,
                 classHashCounts={k: len(v) for k,v in all_hashes.items()}, productTests=0,
                 noApiOrWebMain=True, backendActions=0, wholeF02Accepted=False,
                 whole451Accepted=False, terminalAtUTC=timestamp())
    dump(out / "manifest.json", proof)
    print(pin(out / "manifest.json"), "; statuses", {k:v["actualExit"] for k,v in stages.items()})
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
