"""Prepare the current comparator for the existing owned 21-suite FileStore run."""

import gzip
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile
import zipfile


H = runpy.run_path(str(Path(__file__).with_name("061_compare_definition_contract.py")))
ROOT, TOOLS, MODULE, WORK = (H[key] for key in ("ROOT", "TOOLS", "MODULE", "WORK"))
dump, git, pin, utc = (H[key] for key in ("dump", "git", "pin", "utc"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
PRIOR_RUN = "PG41126-p020-typed-inventory-filestore-v1"
RUN = "PG41278-p020-current-217-owner-v1"
SESSION = "PG41278-CHARACTERIZATION-COMPARISON-DEFINITIONS-217"


def read(path):
    return json.loads(path.read_bytes())


def reference(path):
    return dict(path=str(path), sha256=pin(path))


def prior_path(name, prefix):
    return next(OPS.glob(prefix + "*/" + name))


def prepare(scope):
    starts = [Path(item["path"]) for item in scope["oracleReferences"]]
    assert [pin(path) for path in starts] == [item["sha256"] for item in scope["oracleReferences"]]
    assert git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines() == [scope["source"]] * 2
    old_begin = read(OPS / PRIOR_RUN / "begin.json")
    old_terminal = read(OPS / PRIOR_RUN / "manifest.json")
    old_post = read(prior_path("manifest.json", "PG41128"))
    assert old_post["run"] == old_terminal["run"] == old_begin["run"] == PRIOR_RUN
    assert old_terminal["state"] == "TERMINAL_RETURNED" and old_terminal["actualExit"] == 0
    assert old_post["sameSourceRawAll"] and old_post["completedTests"] == 215
    assert old_post["terminalAtUTC"] > old_terminal["terminalAtUTC"]
    original = read(WORK / PRIOR_RUN / "prepared.json")
    old = original["spec"]
    assert len(old["files"]) == 326 and len(set(old["selectors"])) == len(old["selectors"]) == 21
    assert old["expectedTests"] == 215 and old_post["selectors"] == 21
    assert all(pin(Path(original[key]["path"])) == original[key]["sha256"]
               for key in ("capsule", "runner", "hostControls", "pinnedKey"))
    assert original["expectedBoot"] == old_terminal["terminal"]["bootReceiptSha256"]
    assert old_terminal["terminal"]["actualBackendActions"] == 0
    assert git("rev-parse", f"{old_begin['toolSource']}:{MODULE}/baseline/current") == git(
        "rev-parse", f"{scope['source']}:{MODULE}/baseline/current")
    allowed = {H["TEST"].as_posix(), H["TEST"].as_posix().replace("/tests/java/", "/src/main/java/")
               .replace("ArtifactComparatorTest.java", "ArtifactComparator.java")}
    assert set(git("diff", "--name-only", old_begin["toolSource"], scope["source"],
                   "--", str(MODULE)).decode().splitlines()) == allowed

    work = WORK / RUN
    work.mkdir(mode=0o700)
    snapshot = work / "snapshot"
    with tarfile.open(original["capsule"]["path"], "r:gz") as archive:
        members = archive.getmembers()
        assert len(members) == len(old["files"]) and {row.name for row in members} == set(old["files"])
        assert all(row.isfile() for row in members)
        content = {row.name: archive.extractfile(row).read() for row in members}
    sha = H["hashlib"].sha256
    assert {name: sha(data).hexdigest() for name, data in content.items()} == old["files"]
    checked_baseline = 0
    for name, data in content.items():
        if not name.startswith("snapshot/"):
            continue
        relative = Path(name.removeprefix("snapshot/"))
        assert relative == Path("pom.xml") or relative.is_relative_to(MODULE)
        if relative.is_relative_to(MODULE / "baseline"):
            assert relative.is_relative_to(MODULE / "baseline/current")
            assert data == git("show", f"{scope['source']}:{relative}")
            checked_baseline += 1
        if relative.as_posix() in allowed:
            data = git("show", f"{scope['source']}:{relative}")
            content[name] = data
        destination = work / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    assert checked_baseline == 27

    old_local = read(prior_path("manifest.json", "PG41122"))
    old_work = WORK / old_local["run"]
    env = {"JAVA_HOME": str(TOOLS / "jdk-25.0.4"), "PATH": os.defpath,
           "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    stages = {}

    def execute(kind, args):
        start = utc()
        result = subprocess.run(args, cwd=work, env=env, timeout=100, check=False, capture_output=True)
        stdout, stderr = work / (kind + ".stdout"), work / (kind + ".stderr")
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        stages[kind] = dict(argv=args, startedAtUTC=start, terminalAtUTC=utc(),
                            exitCode=result.returncode, stdout=reference(stdout), stderr=reference(stderr))
        dump(work / (kind + "-terminal.json"), stages[kind])
        assert result.returncode == 0, kind

    package = [arg.replace(str(old_work), str(work)) for arg in old_local["steps"]["compile-tool"]["command"]]
    execute("package", [*package[:-1], "-Dmaven.test.skip=true", "package"])
    target = snapshot / MODULE / "target"
    artifact, = target.glob("schubert-characterization-*.jar")
    classes = {path.relative_to(target / "classes").as_posix(): path.read_bytes()
               for path in (target / "classes").rglob("*.class")}
    with zipfile.ZipFile(artifact) as jar:
        physical = {name: jar.read(name) for name in jar.namelist() if name.endswith(".class")}
    assert len(classes) == 17 and classes == physical and set(classes) == set(old["physical"])
    execute("compile-tests", [arg.replace(str(old_work), str(work))
                              for arg in old_local["steps"]["compile-test"]["command"]])
    test_root = work / "tests"
    tests = {path.relative_to(test_root).as_posix(): path.read_bytes() for path in test_root.rglob("*.class")}
    storage = "dev/codex/schubert/characterization/GateOwnedFileStoreContract.class"
    assert storage not in tests
    tests[storage] = content["testclasses/" + storage]
    assert len(tests) == 37 and set(tests) == set(old["tests"])
    content.update({"classes/" + key: value for key, value in classes.items()})
    content.update({"testclasses/" + key: value for key, value in tests.items()})
    hashes = {name: sha(data).hexdigest() for name, data in content.items()}
    changes = {name for name, value in hashes.items() if old["files"][name] != value}
    assert len(changes) >= 5 and all("ArtifactComparator" in name for name in changes)
    assert {name for name in changes if name.startswith("classes/")} == {
        "classes/dev/codex/schubert/characterization/ArtifactComparator.class",
        "classes/dev/codex/schubert/characterization/ArtifactComparator$ComparisonResult.class",
    }

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(content.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode = len(data), 0o600
            archive.addfile(member, io.BytesIO(data))
    raw = buffer.getvalue()
    capsule = work / "characterization-217.tar.gz"
    payload = gzip.compress(raw, mtime=0)
    assert len(raw) < 12 * 1024**2 and len(payload) < 7 * 1024**2
    capsule.write_bytes(payload)
    runner = work / "runner.py"
    used = Path(original["runner"]["path"]).read_text()
    assertion = "totals == dict(tests=215,"
    assert used.count(assertion) == 1
    runner.write_text(used.replace(assertion, "totals == dict(tests=217,"))
    compile(runner.read_bytes(), str(runner), "exec")
    spec = dict(old, files=hashes, physical={name: sha(body).hexdigest() for name, body in classes.items()},
                tests={name: sha(body).hexdigest() for name, body in tests.items()}, expectedTests=217,
                session=SESSION, capsuleSha256=sha(payload).hexdigest(), size=len(payload),
                rawTarSha256=sha(raw).hexdigest(), rawTarSize=len(raw))
    prepared = dict(original, spec=spec, capsule=reference(capsule), runner=reference(runner))
    dump(work / "prepared.json", prepared)
    out = OPS / RUN
    out.mkdir()
    dump(out / "begin.json", dict(
        run=RUN, source=scope["source"], toolSource=scope["source"], productionCore=scope["productionCoreMain"],
        session=SESSION, expectedTests=217, selectors=old["selectors"], unchangedBaselineTree=True,
        preparationStages=stages, sourceDiff=sorted(changes), samePackagedClasses=17,
        immutableBaselineFixturePaths=checked_baseline,
        physical=spec["physical"], packagingJar=reference(artifact), inputScopeCount=len(hashes),
        existingFileStoreClassPreserved=True, preparedAtUTC=utc(), jobStarted=False, realBackendActions=0,
        prepared=reference(work / "prepared.json"), capsule=reference(capsule), formalDelta=0))
    print("Prepared", len(hashes), len(changes), 217)


if __name__ == "__main__":
    start, = (ROOT / "documents/400_PGPT/470_PMO").glob("601_*/1679_*.json")
    group = read(start)["values"]
    assert group["run"] == RUN
    if sys.argv[1:] == ["prepare"]:
        prepare(group)
    elif sys.argv[1:] == ["execute"]:
        # Reuse enrollment, workspace ownership, known-host, and no-transfer-on-mismatch checks.
        existing = runpy.run_path(str(OPS.parent / "input/5559_p020_current_reader3_filestore.py"))
        existing["execute"](group, session=SESSION, expected_tests=217)
    else:
        raise SystemExit("Choose prepare or execute")
