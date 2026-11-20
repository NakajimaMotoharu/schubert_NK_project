"""Use the new reader on the retained ordinary two-class measurement without running its tests."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
METER = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
BIN = Path("../toolchain/jdk-25.0.4/bin").resolve()


def sha(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def main():
    start_path, = Path("documents/400_PGPT/470_PMO").glob("601_*/1534_*")
    start = read(start_path)["values"]
    refs = [Path(p["path"]) for p in start["oracleReferences"]]
    assert [pin(p) for p in refs] == start["oracleReferences"]
    tool, run, package = map(read, refs[1:])
    assert start["productionCoreMain"] == run["productionCore"] == package["source"]
    assert all(x["actualExit"] == 0 for x in (tool, run, package))
    retained = Path(run["execOriginal"]["path"])
    report = Path(run["rawOriginal"]["path"])
    archive = Path(package["batchArtifact"]["path"])
    assert pin(retained) == run["execOriginal"] and pin(report) == run["rawOriginal"]
    assert pin(archive) == package["batchArtifact"]
    assert tool["toolSourceSha256"] == pin(METER)["sha256"]
    refs_read, = OPS.glob("PG31432-*/compile.json")
    deps = read(refs_read)["dependencies"]
    assert all(pin(Path(p["path"])) == p for p in deps)
    cp = os.pathsep.join(p["path"] for p in deps)
    read_output = OPS / start["run"]
    read_output.mkdir()

    def run_command(cmd):
        words = list(map(str, cmd))
        p = subprocess.run(words, capture_output=True, timeout=40)
        assert p.returncode == 0, p.stderr
        return words, p.stdout

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-original-persisted-") as tmp:
        scratch = Path(tmp)
        source = scratch / METER.name
        source.write_bytes(METER.read_bytes())
        out = scratch / "built"
        command, _ = run_command([BIN/"javac", "--release", "25", "-proc:none", "-Werror",
                                  "-Xlint:all", "-cp", cp, "-d", out, source])
        locator = {row["classPath"]: row["sha256"] for row in run["currentBatchClassBytes"]}
        assert len(locator) == 2
        order = [row["name"] + ".class" for row in run["raw"]]
        assert set(locator) == set(order)
        file_inputs = []
        with ZipFile(archive) as saved:
            assert all(saved.namelist().count(name)==1 for name in order)
            for name in order:
                content = saved.read(name)
                assert sha(content) == locator[name]
                dest = scratch / Path(name).name
                dest.write_bytes(content)
                file_inputs.append(dest)
        actual, raw = run_command([
            BIN/"java", "-cp", f"{out}:{cp}", "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
            "--strict-original-exec", retained, *file_inputs,
        ])
        assert raw == report.read_bytes()
    recorded = read_output / "manifest.json"
    with recorded.open("x") as info:
        json.dump(dict(actualExit=0, productionCore=run["productionCore"], toolSource=tool["toolSource"],
                       exactOriginalStream=pin(retained), originalMeasurement=pin(report),
                       newRawSha256=sha(raw), allRawRowsExact=True, originalSourceAndRun=pin(refs[2]),
                       currentBatchMetadata=pin(refs[3]), testedPhysical=run["currentBatchClassBytes"],
                       strictCompile=command, actualCommand=actual, unmergedSession=run["session"],
                       binaryProductClassesRead=2, productTestsRerun=0, nativeActions=0,
                       whole451=False, formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  info,ensure_ascii=False,indent=2)
        info.write("\n")
    print(pin(recorded))


if __name__ == "__main__":
    main()
