"""Recheck current archived class bytes and the three intended typed-edge changes."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import runpy
import stat
import subprocess
from zipfile import ZipFile


EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PLAN = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117")
GUARD = runpy.run_path(str(Path(__file__).with_name("5331_f02_current_jars_and_edges.py")))


def pin(path):
    path = Path(path)
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    start = read(next(PLAN.glob("776_*")))
    job = start["values"]
    unit = EVIDENCE / job["run"] / "manifest.json"
    manifest = read(unit)
    assert manifest["actualExit"] == manifest["testsExecuted"] == manifest["actualHostActions"] == 0
    assert manifest["sourceCore"] == job["productionCoreMain"] and manifest["gitHead"] == job["source"]
    assert set(manifest["stages"]) == {"compile", "jar", "edges-before", "edges-after"}
    for stage in manifest["stages"].values():
        assert stage["actualExit"] == 0 and all(pin(stage[key]["path"]) == stage[key]
                                                 for key in ("stdout", "stderr"))
    previous = read(job["oracleReferences"][1]["path"])
    current_compile = read(job["oracleReferences"][2]["path"])
    hashes = {}
    for name, jar in manifest["jars"].items():
        keep = Path(jar["artifact"]["path"])
        old = previous["jars"][name]["artifact"]
        assert pin(keep) == jar["artifact"] and pin(old["path"]) == old
        st = keep.lstat()
        assert stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o600
        assert keep.resolve() == keep and st.st_uid == os.getuid()
        with ZipFile(keep) as archive:
            assert archive.testzip() is None
            classes = {path: hashlib.sha256(archive.read(path)).hexdigest()
                       for path in archive.namelist() if path.endswith(".class")}
            assert classes == current_compile["classHashes"][name]
            pom = f"src/schubert-nk-{name}/pom.xml"
            blob = subprocess.check_output(["git", "show", manifest["sourceCore"] + ":" + pom], timeout=20)
            archive_pom = f"META-INF/maven/dev.codex.schubert/schubert-nk-{name}/pom.xml"
            assert archive.read(archive_pom) == blob
        assert keep.lstat() == st
        hashes[name] = jars_entry = dict(physical=len(classes), artifact=jar["artifact"])
        assert jars_entry["physical"] == jar["classes"]
    assert sum(r["physical"] for r in hashes.values()) == 1102
    old_scope = read(next(EVIDENCE.glob("PG40252-f02-storage-jdbc-saved-edges-v1/manifest.json")))
    assert manifest["changedClassesFromOldJars"]["storage"] == []
    assert len(old_scope["violations"]) == 1
    assert old_scope["violations"][0]["target"] == "java.sql.SQLException"
    commands = manifest["stages"]
    before, after = (GUARD["dependency_rows"](commands[s]) for s in ("edges-before", "edges-after"))
    assert before.keys() == after.keys() == manifest["exactNewTypedEdges"].keys()
    actual = {name: dict(added=sorted(after[name]-before[name]), removed=sorted(before[name]-after[name]),
                         identicalCount=len(before[name] & after[name])) for name in sorted(after)}
    assert actual == manifest["exactNewTypedEdges"]
    json_path = EVIDENCE / "PG40328-f02-current-four-jars-independent-v1" / "manifest.json"
    json_path.parent.mkdir()
    data = dict(actualExit=0, source=manifest["gitHead"], productionCore=manifest["sourceCore"],
                packageManifest=pin(unit), qualifiedLocalArtifacts=hashes, measuredDeltas=actual,
                provenPhysical=1102, stillOpenStorageTypedViolation=old_scope["violations"],
                noNewTests=0, sixModuleBuild=False, wholeF02Accepted=False, whole451Accepted=False,
                terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with json_path.open("x") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(json_path))


if __name__ == "__main__":
    main()
