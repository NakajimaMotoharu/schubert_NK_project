"""Assemble the changed Batch JAR with the existing Maven-only authority and join seven CRCs."""

from datetime import datetime, timezone
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
SDK = Path.cwd().parent / "toolchain"
JAVA = SDK / "jdk-25.0.4"
MAVEN = SDK / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
M2 = SDK / "m2/repository"
ALERT = "dev/codex/schubert/nk/batch/monitoring/AlertLifecycle"
QUALIFIED = {ALERT + suffix + ".class" for suffix in
             ("", "$State", "$Event", "$Condition", "$Severity", "$Service", "$CauseClearance")}


def sha(data):
    return sha256(data).hexdigest()


def pin(path):
    path = Path(path)
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_bytes())


def git(*parts):
    return subprocess.check_output(["git", *parts], timeout=60)


def physical(jar):
    names = [name for name in jar.namelist() if name.endswith(".class")]
    assert len(names) == len(set(names)) and all(not n.startswith("META-INF/") for n in names)
    return set(names)


def crc64(data):
    assert data.startswith(bytes.fromhex("cafebabe")) and data[6:8] == bytes.fromhex("0045")
    result = 0
    for byte in data:
        result ^= byte
        for _ in range(8):
            result = (result >> 1) ^ (0xd800000000000000 if result & 1 else 0)
    return result


def main():
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1522_*")
    start = read(start)
    v = start["values"]
    refs = [Path(r["path"]) for r in v["oracleReferences"]]
    assert [pin(p) for p in refs] == v["oracleReferences"]
    source = v["productionCoreMain"]
    saved, tested, independent = map(read, refs[1:])
    assert source == tested["source"] == independent["productionCore"]
    assert all(x["actualExit"] == 0 for x in (saved, tested, independent))
    modules = ["storage", "bootstrap", "batch"]
    assert saved["selectedMavenModules"] == modules
    roots = [f"src/schubert-nk-{name}" for name in modules]
    poms = ["src/schubert-nk-api/pom.xml", "src/schubert-nk-web/pom.xml",
            "program/characterization/pom.xml", "src/schubert-nk-protocol/pom.xml"]
    included = ["pom.xml", ".mvn", *poms, *[f"{mod}/{sub}" for mod in roots for sub in ("pom.xml","src/main")]]
    changed = git("diff", "--name-only", saved["source"], source, "--", *included).decode().splitlines()
    assert changed == [roots[-1] + "/src/main/java/" + ALERT + ".java"]
    library = saved["priorSourceUnchangedLibraryReferences"]
    assert not git("diff", "--name-only", "da20ad7753279ae4e8017593866502d3341ec0e5", source,
                   "--", "pom.xml", ".mvn", *roots[:2], "src/schubert-nk-protocol")
    assert all(pin(item["path"])["sha256"] == item["sha256"] for item in library.values())
    paths = git("archive", "--format=tar", source, "--", *included)
    private = Path.cwd().parent / "pgpt-runs/PG379" / v["run"]
    private.mkdir(mode=0o700)
    out = OPS / v["run"]
    out.mkdir()
    env = {"JAVA_HOME": str(JAVA), "PATH": str(JAVA/"bin")+":"+os.defpath,
           "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    base = [str(MAVEN), "-o", "-B", "-ntp", f"-Dmaven.repo.local={M2}", "-pl", roots[-1]]
    steps = {}

    def call(stage, label, *args):
        cmd = [*base, *args]
        p = subprocess.run(cmd, cwd=stage, env=env, capture_output=True, timeout=100)
        (private / (label+".stdout")).write_bytes(p.stdout)
        (private / (label+".stderr")).write_bytes(p.stderr)
        steps[label] = dict(command=cmd, exit=p.returncode, terminalAtUTC=now(),
                            stdoutSha256=sha(p.stdout), stderrSha256=sha(p.stderr))
        if p.returncode:
            raise SystemExit(p.returncode)

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-current-batch-alert-") as folder:
        stage = Path(folder)
        with tarfile.open(fileobj=io.BytesIO(paths), mode="r:") as tar:
            assert all(i.isfile() or i.isdir() for i in tar)
            tar.extractall(stage, filter="data")
        assert all([p.name for p in (stage/Path(meta).parent).iterdir()] == ["pom.xml"] for meta in poms)
        call(stage, "compile", "-am", "compile")
        call(stage, "jar", "org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar")
        name = "schubert-nk-batch-0.1.0-SNAPSHOT.jar"
        artifact = Path(shutil.copy2(stage / roots[-1] / "target" / name, private / name))

    prior_jar = saved["packaged"]["batch"]
    assert pin(prior_jar["path"])["sha256"] == prior_jar["sha256"]
    wanted = {row["className"]+".class": int(row["crc64"], 16) for row in tested["rawAll"]
              if row["className"]+".class" in QUALIFIED}
    assert set(wanted) == QUALIFIED and independent["ownClassCrcCount"] == 7
    rows = []
    with ZipFile(prior_jar["path"]) as old, ZipFile(artifact) as new:
        old_names, current_names = physical(old), physical(new)
        assert len(old_names) == 646 and current_names == old_names | {ALERT+"$State.class"}
        for item in sorted(QUALIFIED):
            data = new.read(item)
            crc = crc64(data)
            assert wanted[item] == crc
            rows.append(dict(classPath=item, sha256=sha(data), execCrc64=f"{crc:016x}"))
    details = dict(actualExit=0, source=source, run=v["run"], terminalAtUTC=now(),
                   expectedSourceArchiveSha256=sha(paths), previousArtifact=pin(Path(prior_jar["path"])),
                   batchArtifact=pin(artifact), changedMain=changed, selectedMavenModules=modules,
                   metadataOnlyModules=poms, steps=steps, originalClassNames=646, currentClassNames=647,
                   qualifiedAlertPhysical=rows, unrelatedClassEntryBytesReadForMeasurement=0,
                   savedUnchangedLibraryReferences=library, unitOriginal=pin(refs[2]),
                   independent=pin(refs[3]), executedProductTests=0, executedBackendOperations=0,
                   wholeSixBuild=False, wholeF02=False, whole451=False, formalDelta=0)
    m = out / "manifest.json"
    with m.open("x") as file:
        json.dump(details, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(m))


if __name__ == "__main__":
    main()
