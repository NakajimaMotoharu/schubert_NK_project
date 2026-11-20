"""Bind the prepared 211-case capsule to one ordinary haruka run."""

import gzip
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import tarfile


INPUT = Path(__file__)
LEGACY = INPUT.with_name("5343_p020_single_filestore_host.py")
ORIGINAL = runpy.run_path(str(LEGACY))
E, D = ORIGINAL["E"], ORIGINAL["D"]
RUN = "PG40686-p020-current-211-real-filestore-v1"
SESSION = "PG40686-CHARACTERIZATION-211-FILESTORE"
OUT = E / RUN
PRIVATE = Path("../pgpt-runs/PG379").resolve() / RUN.lower()
sha, ref, git, put, read = (ORIGINAL[k] for k in ("sha", "ref", "git", "put", "read"))


def change_once(text, old, new):
    assert text.count(old) == 1
    return text.replace(old, new)


def prepare():
    group = read(next(D.glob("1049_P020*")))["values"]
    assert group["run"] == RUN
    assert all(ref(row["path"]) == row for row in group["oracleReferences"])
    prepared, pmo = (read(row["path"]) for row in group["oracleReferences"][1:3])
    assert group["source"] == git("rev-parse", "HEAD").decode().strip()
    assert group["productionCoreMain"] == prepared["productionCore"]
    assert not git("diff", prepared["source"], group["source"], "--", "pom.xml", "program/characterization", "src")
    assert not git("diff", group["source"], "--", "pom.xml", "program/characterization", "src")
    assert pmo["exit"] == 0 and pmo["host"] == "haruka" and pmo["owner"] == "mini"
    assert pmo["hostKeyChanged"] is False and pmo["requiredBytes"] == ORIGINAL["MIN_BYTES"]
    for item in (prepared["capsule"], prepared["hostInput"], *prepared["publicReceipts"]):
        assert ref(item["path"]) == item
    spec = read(prepared["hostInput"]["path"])
    assert spec["expectedTests"] == prepared["expectedTests"] == 211
    assert len(set(spec["selectors"])) == 21
    assert spec["selectors"].count(ORIGINAL["CASE"]) == 1
    payload = Path(prepared["capsule"]["path"]).read_bytes()
    assert len(payload) == spec["size"] < 7 * 1024**2 and sha(payload) == spec["capsuleSha256"]
    with gzip.GzipFile(fileobj=io.BytesIO(payload)) as stream:
        raw = stream.read(12 * 1024**2)
    assert len(raw) == spec["rawTarSize"] < 12 * 1024**2 and sha(raw) == spec["rawTarSha256"]
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        entries = archive.getmembers()
        assert len(entries) == len(spec["files"]) == 326
        assert {item.name for item in entries} == spec["files"].keys()
        for item in entries:
            assert item.isfile() and not Path(item.name).is_absolute() and ".." not in Path(item.name).parts
            body = archive.extractfile(item).read()
            assert sha(body) == spec["files"][item.name]
            for prefix, hashes in (("classes/", spec["physical"]), ("testclasses/", spec["tests"])):
                if item.name.startswith(prefix):
                    assert sha(body) == hashes[item.name.removeprefix(prefix)]
            if item.name.startswith("snapshot/"):
                assert body == git("show", f'{prepared["source"]}:{item.name.removeprefix("snapshot/")}')
        assert len(spec["physical"]) == 17 and len(spec["tests"]) == 37

    controls = INPUT.with_name("5310_haruka_filestore_owned_runner.py")
    previous = INPUT.with_name("5342_haruka_single_filestore_runner.py")
    old_seed = read(next(E.glob("PG40396-*/begin.json")))
    for path, key in ((controls, "hostControls"), (previous, "runner")):
        assert path.resolve() == Path(old_seed[key]["path"]).resolve()
        assert sha(path.read_bytes()) == old_seed[key]["sha256"]
    runner = change_once(previous.read_text(), "totals == dict(tests=209,", "totals == dict(tests=211,")
    compile(runner, str(previous), "exec")
    PRIVATE.mkdir(mode=0o700)
    target = PRIVATE / "runner.py"
    with target.open("x") as stream:
        stream.write(runner)
    OUT.mkdir()
    put(OUT / "begin.json", dict(
        source=group["source"], previousToolSource=prepared["source"], productionCore=prepared["productionCore"],
        groupStart=read(next(D.glob("1049_P020*")))["eventId"], run=RUN, expectedTests=211,
        capsule=prepared["capsule"], fixture=ref(INPUT.with_name("5341_GateOwnedFileStoreContract.java")),
        runner=ref(target), hostControls=ref(controls), clientFile=ref(INPUT), previousRunner=ref(previous),
        clientBase=ref(LEGACY), pmoPrecheck=group["oracleReferences"][2],
        spec={**spec, "session": SESSION}, previousPreparationSession=spec["session"],
        independentFileInventoryCount=len(entries), terminalAtUTC=ORIGINAL["now"]()))


def execute():
    seed = read(OUT / "begin.json")
    assert seed["clientBase"] == ref(LEGACY)
    assert ref(seed["pmoPrecheck"]["path"]) == seed["pmoPrecheck"]
    pmo = read(seed["pmoPrecheck"]["path"])
    boot = pmo["bootIdSha256"]
    assert len(boot) == 64 and all(c in "0123456789abcdef" for c in boot)
    client = change_once(LEGACY.read_text(), '            assert admission["runAbsent"] is True\n',
                         '            assert admission["runAbsent"] is True\n'
                         '            assert boot_sha(admission["boot"]) == expected_boot\n')
    scope = dict(__file__=str(LEGACY), __name__="fixed_211_haruka",
                 boot_sha=lambda value: hashlib.sha256(value.encode()).hexdigest(), expected_boot=boot)
    exec(compile(client, str(LEGACY), "exec"), scope)
    scope.update(TASK=RUN, SESSION=SESSION, OUT=OUT, STORE=PRIVATE)
    return scope["execute"]()


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["execute"]:
        raise SystemExit(execute())
    else:
        raise SystemExit("Select prepare or execute")
