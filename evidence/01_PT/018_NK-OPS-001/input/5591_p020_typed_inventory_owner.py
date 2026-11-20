"""Prepare the exact comparator after a typed inventory change for one owned normal run."""

from datetime import datetime, timezone
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve()
PRIOR = runpy.run_path(str(HERE.with_name("5559_p020_current_reader3_filestore.py")))
H = runpy.run_path(str(HERE.with_name("5589_p020_typed_inventory.py")))
OPS, WORK, MODULE = (H[k] for k in ("OPS","WORK","MODULE"))
pin, dump, git = (H[k] for k in ("pin","dump","git"))
SESSION = "PG41126-CHARACTERIZATION-TYPED-INVENTORY-215"
SUITES = 21
TESTS = 215


def load(row):
    p = Path(row["path"])
    assert pin(p) == row
    return json.loads(p.read_bytes())


def file_map(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*.class"))}


def prepare(scope):
    refs = scope["oracleReferences"]
    assert all(pin(Path(row["path"])) == row for row in refs)
    local, previous, post, owner, base = map(load, refs[1:6])
    assert local["actualExit"] == previous["actualExit"] == post["actualExit"] == owner["actualExit"] == 0
    assert local["observedTestCounts"] == dict(tests=214, failures=0, errors=0, skipped=0)
    assert post["run"] == previous["run"] and post["completedTests"] == 214
    assert previous["state"] == "TERMINAL_RETURNED" and previous["terminal"]["actualBackendActions"] == 0
    assert previous["terminal"]["bootReceiptSha256"] == owner["ownerReceipt"]["bootIdSha256"]
    assert owner["ownerReceipt"]["ownerUid"] == 1000 and owner["ownerReceipt"]["matchesLastApprovedBootReceipt"]
    assert pin(Path(owner["pinnedHostKey"]["path"])) == owner["pinnedHostKey"]
    assert git("rev-parse","HEAD","origin/dev-foundation").decode().splitlines() == [scope["source"]]*2
    assert not git("diff","--name-only",local["source"],scope["source"],"--",str(MODULE))
    assert local["productionCore"] == scope["productionCoreMain"]
    previous_begin = load(post["terminalEvidence"][0])
    local_work = WORK/local["run"]
    snap = local_work/"snapshot"
    older_work = WORK/previous["run"]
    older_prepared = json.loads((older_work/"prepared.json").read_bytes())
    original_spec = older_prepared["spec"]
    assert original_spec["expectedTests"] == 214
    assert previous_begin["inputScopeCount"] == len(original_spec["files"]) == 326
    assert len(original_spec["selectors"]) == len(set(original_spec["selectors"])) == SUITES
    fixture = Path(previous_begin["compiledFileStore"]["path"])
    assert pin(fixture) == previous_begin["compiledFileStore"]
    contents = {}
    for name, expected in local["inputSha256"].items():
        path = snap/name
        assert pin(path)["sha256"] == expected
        contents["snapshot/"+name] = path.read_bytes()
    classes = file_map(snap/MODULE/"target/classes")
    tests = file_map(local_work/"tests")
    assert {n: sha256(body).hexdigest() for n, body in classes.items()} == local["physical"]
    file_store = PRIOR["FILESTORE"].replace(".","/")+".class"
    assert file_store not in tests and sha256(fixture.read_bytes()).hexdigest() == original_spec["tests"][file_store]
    tests[file_store] = fixture.read_bytes()
    assert len(classes) == 17 and len(tests) == 37
    contents.update({"classes/"+name: body for name,body in classes.items()})
    contents.update({"testclasses/"+name: body for name,body in tests.items()})
    before = WORK/previous["run"]/"characterization-214.tar.gz"
    assert pin(before) == older_prepared["capsule"]
    with tarfile.open(before, "r:gz") as archive:
        for item in archive.getmembers():
            if item.name.startswith("sdk/"):
                assert item.isfile()
                contents[item.name] = archive.extractfile(item).read()
                assert sha256(contents[item.name]).hexdigest() == original_spec["files"][item.name]
    hashes = {key: sha256(body).hexdigest() for key, body in contents.items()}
    assert hashes.keys() == original_spec["files"].keys()
    changed = sorted(name for name, sha in hashes.items() if original_spec["files"][name] != sha)
    assert changed and all("GateCli" in name for name in changed)

    work, out = WORK/scope["run"], OPS/scope["run"]
    work.mkdir(mode=0o700)
    out.mkdir()
    packed = io.BytesIO()
    with tarfile.open(fileobj=packed, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, body in sorted(contents.items()):
            entry = tarfile.TarInfo(name)
            entry.size, entry.mode = len(body), 0o600
            archive.addfile(entry, io.BytesIO(body))
    raw = packed.getvalue()
    payload = gzip.compress(raw, mtime=0)
    assert len(raw) < 12*1024**2 and len(payload) < 7*1024**2
    capsule = work/"characterization-215.tar.gz"
    capsule.write_bytes(payload)
    spec = dict(original_spec, files=hashes, physical=local["physical"],
                tests={name: sha256(body).hexdigest() for name, body in tests.items()},
                capsuleSha256=sha256(payload).hexdigest(), size=len(payload),
                rawTarSha256=sha256(raw).hexdigest(), rawTarSize=len(raw), session=SESSION, expectedTests=TESTS)
    runner = Path(refs[6]["path"]).read_text()
    expected = "totals == dict(tests=209,"
    assert runner.count(expected) == 1 and pin(Path(base["hostControls"]["path"])) == base["hostControls"]
    runtime = work/"runner.py"
    runtime.write_text(runner.replace(expected, f"totals == dict(tests={TESTS},"))
    compile(runtime.read_bytes(), str(runtime), "exec")
    dump(work/"prepared.json", dict(spec=spec, capsule=pin(capsule), runner=pin(runtime),
                                    hostControls=base["hostControls"], expectedBoot=owner["ownerReceipt"]["bootIdSha256"],
                                    pinnedKey=owner["pinnedHostKey"]))
    dump(out/"begin.json", dict(
        source=scope["source"], toolSource=local["source"], productionCore=local["productionCore"],
        run=scope["run"], session=SESSION, expectedTests=TESTS, selectors=spec["selectors"],
        localEvidence=refs[1], previousOwnerAdmission=refs[4], previousRun=refs[2],
        sourceDiff=changed, inputScopeCount=len(hashes), compiledFileStore=pin(fixture),
        preparatoryArtifact=pin(capsule), hostControls=base["hostControls"], runner=pin(runtime),
        preparedAtUTC=datetime.now(timezone.utc).isoformat(), jobStarted=False, realBackendActions=0))
    print("prepared",len(hashes),len(changed),TESTS)


if __name__=="__main__":
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1558_*.json")
    scope = json.loads(start.read_bytes())["values"]
    if sys.argv[1:] == ["prepare"]:
        prepare(scope)
    elif sys.argv[1:] == ["execute"]:
        PRIOR["execute"](scope, session=SESSION, expected_tests=TESTS)
    else:
        raise SystemExit("Choose prepare or execute")
