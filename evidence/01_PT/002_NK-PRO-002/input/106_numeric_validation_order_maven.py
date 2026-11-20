"""Run the complete allowed Protocol module once after the codec ordering correction."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[4]
H = runpy.run_path(str(ROOT / "evidence/01_PT/018_NK-OPS-001/input/5388_f03_protocol_current_maven.py"))
MODULE, PMO, OPS, JAVA, MAVEN, CACHE = (H[key] for key in
    ("MODULE", "PMO", "OPS", "JAVA", "MAVEN", "CACHE"))
pin, write, git = (H[key] for key in ("pin", "write", "git"))
RUN = "PG41302-protocol-numeric-full-maven-v1"


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    start = json.loads(next(PMO.glob("1697_*.json")).read_bytes())["values"]
    previous_path = Path(start["oracleReferences"][2]["path"])
    previous = json.loads(previous_path.read_bytes())
    assert previous["actualExit"] == 0 and previous["tests"] == 170 and previous["suites"] == 39
    candidate = git("rev-parse", "HEAD").decode().strip()
    assert git("rev-parse", "HEAD", "origin/main").decode().splitlines() == [candidate, start["canonicalDesignSource"]]
    edits = git("diff", "--name-only", "-z", previous["source"], candidate, "--", str(MODULE)).decode().split("\0")[:-1]
    assert len(edits) == 2 and {Path(path).name for path in edits} == {"FieldCodec.java", "FieldCodecTest.java"}
    assert not git("diff", "--name-only", previous["source"], candidate, "--", "pom.xml")
    main = [path for path in git("diff", "--name-only", start["productionCoreMain"], candidate,
                                 "--", ":(glob)src/**/src/main/**").decode().splitlines()]
    assert len(main) == 1 and Path(main[0]).stem == "FieldCodec"
    out = OPS / RUN
    out.mkdir()
    assert shutil.disk_usage("/dev/shm").free >= 256 * 1024**2
    local = Path(tempfile.mkdtemp(dir="/dev/shm", prefix="pgpt-protocol-numeric-order-"))
    inventory = {}
    for rel, blob in H["tracked_files"](candidate):
        dest = local / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(git("show", f"{candidate}:{rel}"))
        inventory[str(rel)] = dict(gitBlob=blob, sha256=pin(dest)["sha256"])
    assert sum("/src/main/java/" in path for path in inventory) == 169
    files = out / "tracked-inputs.json"
    write(files, inventory)
    home = local / "isolated-home"
    home.mkdir(mode=0o700)
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo", "HOME": str(home),
           "JAVA_HOME": str(JAVA), "MAVEN_SKIP_RC": "true",
           "MAVEN_OPTS": f"-Duser.home={home} -Djava.io.tmpdir={local}"}
    argv = [str(MAVEN), "-B", "-o", "-ntp", "-Dstyle.color=never",
            "-Dmaven.repo.local=" + str(CACHE), "-f", str(local / MODULE / "pom.xml"), "verify"]
    begin = out / "begin.json"
    write(begin, dict(run=RUN, source=candidate, previous=pin(previous_path),
                      baseProductionCore=start["productionCoreMain"], sourceDelta=edits,
                      command=argv, input=pin(files), java=pin(JAVA / "bin/java"), maven=pin(MAVEN),
                      expectedTests=171, expectedSuites=39, startedAtUTC=utc(), ownerOnly=True))
    private = local / "original-maven.log"
    with private.open("x") as stream:
        with subprocess.Popen(argv, cwd=local, env=env, stdout=stream, stderr=subprocess.STDOUT) as child:
            write(out / "binding.json", dict(run=RUN, process=child.pid, local=str(local),
                                            source=candidate, startedAtUTC=utc()))
            print("Started", RUN, child.pid, local, flush=True)
            exit_code = child.wait()
    raw = private.read_bytes()
    output = out / "maven-summary.txt"
    prefixes = ("[INFO] --- ", "[INFO] Tests run:", "[INFO] BUILD ", "[INFO] Total time:",
                "[INFO] All coverage checks have been met.", "[INFO] Compiling ",
                "[INFO] BugInstance size is ", "[INFO] Error size is ")
    output.write_text("\n".join(line.replace(str(local), "<FROZEN_PROTOCOL>")
                                for line in raw.decode("utf-8", "replace").splitlines()
                                if line.startswith(prefixes)) + "\n")
    target = local / MODULE / "target"
    terminal = out / "terminal.json"
    write(terminal, dict(run=RUN, source=candidate, actualExit=exit_code, terminalAtUTC=utc(),
        begin=pin(begin), work=str(local), logHash=hashlib.sha256(raw).hexdigest(), summary=pin(output),
        surefireReports=len(list((target / "surefire-reports").glob("TEST-*.xml"))),
        jacocoPresent=(target / "jacoco.exec").exists(),
        actualIntegrationOrRemoteJobs=0, whole451=False, formalNewAcceptance=0))
    print(pin(terminal), exit_code, flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
