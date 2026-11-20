"""Recheck prior genuine single streams without re-running either test cohort."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

HERE = Path(__file__)
H = runpy.run_path(str(HERE.with_name("5593_p01808_original_name_binding.py")))
OPS, BIN, METER, CLASS = [H[n] for n in ("OPS","BIN","METER","CLASS")]
pin, read, sha = (H[n] for n in ("pin","read","sha"))


def find(id):
    file, = OPS.glob(f"{id}-*/manifest.json")
    return file, read(file)


def pinned(payload):
    p = Path(payload["path"])
    assert pin(p) == payload
    return p


def main():
    green_path, green = find("PG41132")
    old_path, old = find("PG41088")
    chr_path, chr_proof = find("PG41128")
    assert green["observedUnderRejection"] == 0 and green["caseCount"] == 10
    assert green["toolSourceSha256"] == pin(METER)["sha256"]
    assert all(row["actualExit"] == 0 for row in (old, chr_proof))
    source_proof = read(pinned(old["originalSourceAndRun"]))
    archive = pinned(read(pinned(old["currentBatchMetadata"]))["batchArtifact"])
    ordinary_exec = pinned(old["exactOriginalStream"])
    ordinary_raw = pinned(old["originalMeasurement"])
    chr_exec = pinned(chr_proof["returnedEvidence"]["combined.exec"])
    chr_raw = pinned(chr_proof["rawOutput"])
    chr_run = read(pinned(chr_proof["terminalEvidence"][0]))
    chr_local = read(pinned(chr_run["localEvidence"]))
    chr_files = [Path(arg) for arg in chr_proof["rawCommand"][5:]]
    chr_classes = chr_files[0].parents[4]
    assert {str(p.relative_to(chr_classes)): pin(p)["sha256"] for p in chr_files} == chr_local["physical"]
    libs, = OPS.glob("PG31432-*/compile.json")
    dependencies = [pinned(p) for p in read(libs)["dependencies"]]
    cp = os.pathsep.join(map(str,dependencies))

    def run(args):
        command = list(map(str,args))
        process = subprocess.run(command, capture_output=True, timeout=60, check=False)
        assert process.returncode == 0, (process.returncode, sha(process.stderr))
        return command, process.stdout

    results = []
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-original-name-verify-") as temp:
        scratch = Path(temp)
        classes = scratch/"classes"
        compiler, _ = run([BIN/"javac", "--release", "25", "-proc:none", "-Xlint:all", "-Werror",
                          "-cp", cp, "-d", classes, METER])
        order = [row["name"]+".class" for row in source_proof["raw"]]
        expected = {row["classPath"]: row["sha256"] for row in source_proof["currentBatchClassBytes"]}
        assert len(order)==2 and set(order) == set(expected)
        ordinary_files = []
        with ZipFile(archive) as original:
            for path in order:
                assert original.namelist().count(path) == 1
                body = original.read(path)
                assert sha(body) == expected[path]
                out = scratch/Path(path).name
                out.write_bytes(body)
                ordinary_files.append(out)
        for source, stream, previous_table, files in [
            (old_path, ordinary_exec, ordinary_raw, ordinary_files),
            (chr_path, chr_exec, chr_raw, chr_files),
        ]:
            command, measured = run([BIN/"java","-cp",f"{classes}:{cp}",CLASS,
                                     "--strict-original-exec",stream,*files])
            assert measured == previous_table.read_bytes()
            results.append(dict(source=pin(source), originalExec=pin(stream),
                                originalRaw=pin(previous_table), matchedRows=len(measured.splitlines()),
                                suppliedPhysicalClasses=len(files), actualExit=0, command=command))
    out = OPS/"PG41134-p01808-original-name-genuine-streams-v1"
    out.mkdir()
    result = out/"manifest.json"
    with result.open("x") as file:
        json.dump(dict(actualExit=0, tool=pin(green_path), toolSource=green["toolSource"],
                       productionCore=green["productionCore"], results=results, compile=compiler,
                       ordinaryTestsReplayed=0, cohortsMerged=False, actualNative=0, formalDelta=0,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),file,ensure_ascii=False,indent=2)
        file.write("\n")
    print(pin(result),len(results))


if __name__=="__main__":
    main()
