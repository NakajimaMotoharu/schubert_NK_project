"""Build the changed Batch artifact with the previously admitted Maven assembly."""

from datetime import datetime, timezone
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
from zipfile import ZipFile


def hash_bytes(data):
    return sha256(data).hexdigest()


def hash_file(path):
    return hash_bytes(path.read_bytes())


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    repo = Path.cwd()
    tools = repo.parent / "toolchain"
    jdk = tools / "jdk-25.0.4"
    maven = tools / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    m2 = tools / "m2/repository"
    start = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1443_*")).read_bytes())
    v = start["values"]
    source = v["productionCoreMain"]
    admissions = [Path(r["path"]) for r in v["oracleReferences"]]
    assert [hash_file(p) for p in admissions] == [r["sha256"] for r in v["oracleReferences"]]
    saved = json.loads(admissions[1].read_bytes())
    typed = json.loads(admissions[2].read_bytes())
    assert typed['source'] == source and typed['actualExit'] == 0
    modules = ["storage", "bootstrap", "batch"]
    assert saved["selectedMavenModules"] == modules and saved["actualExit"] == 0
    roots = [f"src/schubert-nk-{name}" for name in modules]
    poms_only = ["src/schubert-nk-api/pom.xml", "src/schubert-nk-web/pom.xml",
                 "program/characterization/pom.xml", "src/schubert-nk-protocol/pom.xml"]
    paths = ["pom.xml", ".mvn", *poms_only]
    paths.extend(f"{module}/{child}" for module in roots for child in ("pom.xml", "src/main"))
    archive = git("archive", "--format=tar", source, "--", *paths)
    prior = saved["source"]
    unchanged_pinned = [f"src/schubert-nk-{name}" for name in ("protocol","storage","bootstrap")]
    assert not git("diff","--name-only",prior,source,"--","pom.xml",".mvn",*unchanged_pinned)
    changed = git("diff", "--name-only", prior, source, "--", *paths).decode().splitlines()
    assert changed == [
        "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/MonitoringModePolicy.java"
    ]
    private = repo.parent / "pgpt-runs/PG379" / v["run"]
    private.mkdir(mode=0o700)
    result = Path("evidence/01_PT/018_NK-OPS-001/evidence") / v["run"]
    result.mkdir()
    steps, artifacts = {}, {}
    started = now()
    env = {"JAVA_HOME": str(jdk), "PATH": str(jdk/"bin")+":"+os.defpath,
           "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    modules_arg = roots[-1]
    base = [str(maven), "-o", "-B", "-ntp", f"-Dmaven.repo.local={m2}", "-pl", modules_arg]
    with tempfile.TemporaryDirectory(prefix="pg40988-", dir="/dev/shm") as directory:
        stage = Path(directory)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as stream:
            assert all(entry.isfile() or entry.isdir() for entry in stream)
            stream.extractall(stage, filter="data")
        assert all([p.name for p in (stage/Path(meta).parent).iterdir()]==["pom.xml"] for meta in poms_only)
        assert not list((stage/"src").rglob("*.class"))
        def call(name, args):
            cmd = [*base,*args]
            t = now()
            p = subprocess.run(cmd, cwd=stage, env=env, capture_output=True, timeout=120)
            (private/f"{name}.stdout").write_bytes(p.stdout)
            (private/f"{name}.stderr").write_bytes(p.stderr)
            lines = p.stdout.decode(errors="replace").splitlines()
            steps[name] = dict(command=cmd, beginUTC=t,endUTC=now(),exit=p.returncode,
                               reactorSummary=[line for line in lines if " SUCCESS [" in line
                                               and line.startswith("[INFO]")],
                               stdoutSha256=hash_bytes(p.stdout),stderrSha256=hash_bytes(p.stderr))
            if p.returncode:
                print(name, p.returncode, [line for line in lines if line.startswith("[ERROR]")][-10:])
            return p.returncode
        code = call("compile",["-am","compile"])
        if code == 0:
            code = call("jar",["org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar"])
        if code == 0:
            for name, module in [("batch", roots[-1])]:
                jar = stage / module / "target" / f"schubert-nk-{name}-0.1.0-SNAPSHOT.jar"
                assert jar.is_file() and jar.stat().st_size>0
                retained = Path(shutil.copy2(jar,private/jar.name))
                artifacts[name] = dict(path=str(retained),fileBytes=retained.stat().st_size,
                                       sha256=hash_file(retained))
    checked = {}
    if code == 0:
        prefix = changed[0].split("/src/main/java/")[1].removesuffix(".java")
        allowed_names = {prefix + suffix + ".class"
                         for suffix in ("", "$DetailService", "$RetentionConfiguration")}
        qualified = {row["path"].split("/target/classes/", 1)[1]: row
                     for row in typed["actualPhysical"] if "/target/classes/" in row["path"]}
        assert allowed_names == set(qualified)
        with ZipFile(artifacts["batch"]["path"]) as jar:
            for member in sorted(allowed_names):
                item = qualified[member]
                assert hash_file(Path(item["path"])) == item["sha256"]
                class_hash = hash_bytes(jar.read(member))
                checked[member] = {"sha256": class_hash, "matchesIndependentTypedAndScopedPt": class_hash == item["sha256"]}
        if not all(row["matchesIndependentTypedAndScopedPt"] for row in checked.values()):
            code = 1
    evidence = dict(actualExit=code,source=source,priorCore=prior,startEvent=start["eventId"],
                    startedAtUTC=started,terminalAtUTC=now(),sourceArchiveSha256=hash_bytes(archive),
                    changedMain=changed,selectedMavenModules=modules,metadataOnlyModules=poms_only,
                    steps=steps,packaged=artifacts,productTestsStarted=0,whole451=False,
                    priorSourceUnchangedLibraryReferences=saved["priorSourceUnchangedLibraryReferences"],
                    approvedPhysicalComparisons=checked,
                    priorSourceUnchangedLibrariesPackagedAgain=0,
                    wholeSixBuild=False,jarStaticInvocations=0,heldClassfilesProvidedToAnalyzers=0,
                    externalOperations=0,formalDelta=0)
    m = result/"manifest.json"
    m.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n")
    print(code,len(artifacts),hash_file(m))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
