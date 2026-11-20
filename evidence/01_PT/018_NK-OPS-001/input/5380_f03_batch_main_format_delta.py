"""Verify the exact Batch Main formatter delta without rerunning unchanged sources."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PMO = Path("documents/400_PGPT/470_PMO")
BATCH = "src/schubert-nk-batch/src/main/java/"


def read(path):
    return json.loads(Path(path).read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    path = Path(path)
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args])


def keep(path, payload):
    with path.open("x") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return pin(path)


def main():
    start_file = next(PMO.glob("601_*/914_*"))
    start = read(start_file)["values"]
    references = start["oracleReferences"]
    assert all(pin(p["path"]) == p for p in references)
    prior = read(references[1]["path"])
    for key in ("physicalSourceProof", "formatTerminal"):
        assert pin(prior[key]["path"]) == prior[key]
    old = read(prior["physicalSourceProof"]["path"])
    terminal = read(prior["formatTerminal"]["path"])
    assert terminal["actualExit"] == prior["formatFilesRequired"] == 0
    assert all(pin(p["path"]) == p for p in old["toolArtifacts"])
    command = old["checks"]["format"][:7]
    assert command[-3:] == ["--skip-reflowing-long-strings", "--dry-run", "--set-exit-if-changed"]
    batch_before = {name: sha for name, sha in old["sourceIds"].items() if name.startswith(BATCH)}
    core = start["productionCoreMain"]
    names = git("ls-tree", "-rz", "--name-only", core, "--", BATCH).decode().split("\0")[:-1]
    assert len(names) == prior["modules"]["batch"] == 200
    assert set(names) == set(batch_before)
    changed = set(git("diff", "--no-renames", "--name-only", prior["source"], core,
                      "--", BATCH).decode().splitlines())
    assert changed and changed <= set(names)
    assert all(name.endswith(".java") and Path(name).stem not in {
        "TemporaryInfrastructureException", "FingerprintKeyRing",
        "ResponseSnapshotCodec", "WebStartupException",
    } for name in names)
    current = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-batch-format-") as folder:
        sandbox = Path(folder)
        for name in names:
            data = git("show", f"{core}:{name}")
            sha = digest(data)
            assert (sha != batch_before[name]) == (name in changed)
            current[name] = sha
            if name in changed:
                path = sandbox / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        actual_command = [*command, *sorted(changed)]
        first_validation = subprocess.run(
            actual_command,
            cwd=sandbox,
            env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
            capture_output=True,
            timeout=90,
            check=False,
        )
        unchanged_by_formatter = all(digest((sandbox / name).read_bytes()) == current[name]
                                     for name in changed)
    output = OPS / start["run"]
    output.mkdir()
    for suffix in ("stdout", "stderr"):
        (output / ("formatter." + suffix)).write_bytes(getattr(first_validation, suffix))
    passes = first_validation.returncode == 0 and not first_validation.stdout and unchanged_by_formatter
    record = {
        "actualExit": 0 if passes else 1,
        "source": start["source"],
        "productionCore": core,
        "begin": pin(start_file),
        "priorFormatter": prior["formatTerminal"],
        "priorSource": prior["source"],
        "command": actual_command,
        "actualFormatterExit": first_validation.returncode,
        "formatOptionsUnchanged": True,
        "sourceFilesUntouched": unchanged_by_formatter,
        "coveredByExactPriorBytes": len(names) - len(changed),
        "newlyCheckedPaths": sorted(changed),
        "coveredByCurrentFormatProcess": len(changed) if passes else 0,
        "batchMainTotal": len(names),
        "currentFileInventory": keep(output / "sources.json", current),
        "stdout": pin(output / "formatter.stdout"),
        "stderr": pin(output / "formatter.stderr"),
        "productTests": 0,
        "productRuntimeActions": 0,
        "typedAnalysis": False,
        "wholeF03Accepted": False,
        "whole451Accepted": False,
        "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
    }
    print(keep(output / "manifest.json", record), len(names), len(changed), passes)
    return record["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
