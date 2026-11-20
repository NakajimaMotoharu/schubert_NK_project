"""Run the current standalone Protocol product module once in a fresh frozen tree."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path.cwd()
MODULE = Path("src/schubert-nk-protocol")
PMO = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
JAVA = ROOT.parent / "toolchain/jdk-25.0.4"
MAVEN = Path("/home/mini/.m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn")
CACHE = ROOT.parent / "toolchain/m2/repository"


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, data):
    with path.open("x") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def git(*args):
    return subprocess.check_output(["git", *args])


def tracked_files(source):
    listing = git("ls-tree", "-r", "-z", source, "--", "pom.xml", str(MODULE))
    for entry in listing.decode().rstrip("\0").split("\0"):
        identity, name = entry.split("\t", 1)
        mode, kind, blob = identity.split()
        assert kind == "blob" and mode in {"100644", "100755"}
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert path == Path("pom.xml") or path.is_relative_to(MODULE)
        yield path, blob


def main():
    start = json.loads(next(PMO.glob("980_*")).read_bytes())["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in start["oracleReferences"])
    source = start["source"]
    core = start["productionCoreMain"]
    assert not git("diff", "--name-only", core, source, "--", str(MODULE / "src/main"), "pom.xml", str(MODULE / "pom.xml"))
    prior = json.loads(Path(start["oracleReferences"][1]["path"]).read_bytes())
    edits = git("diff", "--name-only", "-z", prior["source"], source, "--", str(MODULE)).decode().strip("\0").split("\0")
    names = {"LogSearchWireUnicodeTest.java", "QuestionNotificationWireTest.java", "UserCommandWireUnicodeTest.java",
             "UserListReplyWireTest.java"}
    assert len(edits) == 4 and {Path(p).name for p in edits} == names
    assert all((JAVA / "bin" / name).is_file() for name in ("java", "javac")) and MAVEN.is_file() and CACHE.is_dir()
    out = OPS / start["run"]
    out.mkdir()
    disk = shutil.disk_usage("/dev/shm")
    assert disk.free >= 256 * 1024**2
    local = Path(tempfile.mkdtemp(dir="/dev/shm", prefix="pgpt-current-protocol-full-"))
    proof = {}
    for path, blob in tracked_files(source):
        data = git("show", f"{source}:{path}")
        dest = local / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        proof[str(path)] = dict(gitBlob=blob, sha256=pin(dest)["sha256"])
    assert sum("/src/main/java/" in path for path in proof) == 169
    files = out / "tracked-inputs.json"
    write(files, proof)
    home = local / "isolated-home"
    home.mkdir()
    env = {key: value for key, value in os.environ.items() if key in {"LANG", "PATH", "TZ"}}
    env.update(HOME=str(home), JAVA_HOME=str(JAVA), MAVEN_SKIP_RC="true",
               MAVEN_OPTS=f"-Duser.home={home} -Djava.io.tmpdir={local}")
    command = [
        str(MAVEN), "-B", "-o", "-ntp", "-Dstyle.color=never",
        "-Dmaven.repo.local=" + str(CACHE), "-f", str(local / MODULE / "pom.xml"), "verify",
    ]
    begin = out / "begin.json"
    write(begin, dict(command=command, source=source, productionCore=core, sourceDelta=edits,
                      sourceInventory=pin(files), java=pin(JAVA / "bin/java"), maven=pin(MAVEN),
                      isolatedPermissions=oct(local.stat().st_mode & 0o777), started=datetime.now(timezone.utc).isoformat(),
                      allowedModules=["protocol"], cacheMode="existing local, offline", expectedMainSourceCount=169))
    private_log = local / "original-maven.log"
    with private_log.open("x") as log:
        with subprocess.Popen(command, cwd=local, env=env, stdout=log, stderr=subprocess.STDOUT) as process:
            print("Started product Module Protocol", process.pid, local, flush=True)
            result = process.wait()
    full_log = private_log.read_bytes()
    filtered = out / "maven-steps.txt"
    prefixes = ("[INFO] --- ", "[INFO] Tests run:", "[INFO] BUILD ", "[INFO] Total time:",
                "[INFO] All coverage checks have been met.", "[INFO] Compiling ", "[INFO] Analyzed bundle",
                "[INFO] BugInstance size is ", "[INFO] Error size is ")
    lines = [line.replace(str(local), "<FROZEN_PROTOCOL>") for line in full_log.decode("utf-8", "replace").splitlines()
             if line.startswith(prefixes)]
    filtered.write_text("\n".join(lines) + "\n")
    target = local / MODULE / "target"
    result_file = out / "terminal.json"
    write(result_file, dict(source=source, productionCore=core, actualExit=result,
                            terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                            begin=pin(begin), retainedPrivateDirectory=str(local),
                            mavenLogDigest=hashlib.sha256(full_log).hexdigest(), filteredMavenSteps=pin(filtered),
                            surefireXmlCount=len(list((target / "surefire-reports").glob("TEST-*.xml"))),
                            coverageExecExists=(target / "jacoco.exec").is_file(),
                            coverageXmlExists=(target / "site/jacoco/jacoco.xml").is_file(),
                            rawProductJarExists=(target / "schubert-nk-protocol-0.1.0-SNAPSHOT.jar").is_file(),
                            spotbugsXmlExists=(target / "spotbugsXml.xml").is_file(),
                            blockedOrExternalModulesStarted=0, whole451Accepted=False))
    print(pin(result_file), result, flush=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
