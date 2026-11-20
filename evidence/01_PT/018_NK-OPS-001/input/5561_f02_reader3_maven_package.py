"""Package only the current comparison tool and match every class to the tested bytes."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile


ROOT = Path("evidence/01_PT/018_NK-OPS-001/evidence")
MODULE = Path("program/characterization")


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=30)


def main():
    start = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1491_*.json"))
    group = json.loads(start.read_bytes())
    scope = group["values"]
    refs = scope["oracleReferences"]
    assert all(pin(Path(row["path"])) == row for row in refs)
    prior, current, independent = [json.loads(Path(row["path"]).read_bytes()) for row in refs[1:]]
    assert prior["actualExit"] == current["testExit"] == independent["actualExit"] == 0
    assert independent["completedTests"] == 214 and independent["sameSourceRawAll"]
    assert current["source"] == independent["toolSource"]
    head = scope["source"]
    assert git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines() == [head, head]
    assert not git("diff", "--name-only", current["source"], head, "--", "pom.xml", str(MODULE))
    files = [Path(row["path"]) for row in prior["inputs"]]
    assert len(files) == len(set(files)) == 14
    assert sum(path.name == "pom.xml" for path in files) == 8
    assert all(path.name == "pom.xml" or path.is_relative_to(MODULE / "src/main/java") for path in files)
    work = Path("../pgpt-runs/PG379").resolve() / scope["run"]
    work.mkdir(mode=0o700)
    staging = work / "source"
    inputs = []
    for path in files:
        body = git("show", f"{head}:{path}")
        if str(path) in current["inputSha256"]:
            assert sha256(body).hexdigest() == current["inputSha256"][str(path)]
        dest = staging / path
        dest.parent.mkdir(exist_ok=True, parents=True)
        dest.write_bytes(body)
        inputs.append(dict(path=str(path), sha256=sha256(body).hexdigest()))
    assert not (staging / MODULE / "baseline").exists()
    assert not (staging / MODULE / "tests").exists()
    cmd = prior["command"]
    for index, argument in enumerate(cmd):
        if argument == "-f":
            assert cmd[index+1] == "pom.xml"
    assert cmd[-1] == "package" and "-o" in cmd and "-Dmaven.test.skip=true" in cmd
    tc = Path("../toolchain").resolve()
    jdk = tc / "jdk-25.0.4"
    env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    started = utc()
    run = subprocess.run(cmd, cwd=staging, env=env, capture_output=True, check=False, timeout=100)
    logs = {}
    for name, body in (("stdout", run.stdout), ("stderr", run.stderr)):
        log = work / (name + ".txt")
        log.write_bytes(body)
        logs[name] = pin(log)
    term = utc()
    out = ROOT / scope["run"]
    out.mkdir()
    artifact = None
    checked = {}
    if run.returncode == 0:
        jar, = (staging / MODULE / "target").glob("schubert-characterization-*.jar")
        artifact = Path(shutil.copy2(jar, work / jar.name))
        with ZipFile(artifact) as packaged:
            names = [name for name in packaged.namelist() if name.endswith(".class")]
            assert len(names) == len(set(names)) == 17 and set(names) == current["physical"].keys()
            for name in sorted(names):
                body = packaged.read(name)
                assert body[:4] == b"\xca\xfe\xba\xbe"
                major = int.from_bytes(body[6:8], "big")
                value = sha256(body).hexdigest()
                checked[name] = dict(major=major, sha256=value, matchesMeasuredClass=value == current["physical"][name])
    passed = run.returncode == 0 and len(checked) == 17 and all(
        row["major"] == 69 and row["matchesMeasuredClass"] for row in checked.values())
    manifest = dict(actualExit=0 if passed else 1, mavenExit=run.returncode, source=head,
                    toolSource=current["source"], productionCore=scope["productionCoreMain"],
                    startEvent=group["eventId"], run=scope["run"], startedAtUTC=started, terminalAtUTC=term,
                    command=cmd, java="25.0.4", maven="3.9.12", productPomCount=6, productSourcesProvided=0,
                    inputs=inputs, buildLogs=logs, testedInputs=refs[2:], artifact=pin(artifact) if artifact else None,
                    classComparisons=checked, productTestsStarted=0, toolTestsStarted=0, chrStarted=0,
                    baselineFileContentsRead=0, wholeF02=False, whole451=False, formalDelta=0)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print("Maven", run.returncode, "byte comparisons", len(checked), "matched", passed)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
