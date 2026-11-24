"""Validate the WBS inventory reference in the Git index before publication."""

import argparse
import json
from pathlib import Path
import runpy
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
_GUARD = runpy.run_path(str(ROOT / (
    "evidence/01_PT/018_NK-OPS-001/input/580_wbs_inventory_reference_guard.py"
)))
INVENTORY = _GUARD["INVENTORY"]
ACCEPTANCE = _GUARD["ACCEPTANCE"]
ALLOWED_INDEX_MODES = {b"100644", b"100755"}
JAVA_ROOTS = {
    f"src/schubert-nk-{module}/src/main/java/": module
    for module in ("protocol", "storage", "bootstrap", "api", "web", "batch")
}


def read_index_blob(root: Path, path: str) -> bytes:
    command = ["git", "ls-files", "--stage", "-z", "--", path]
    entries = subprocess.check_output(command, cwd=root, timeout=10).split(b"\0")[:-1]
    if len(entries) != 1:
        raise ValueError(f"expected one staged WBS blob: {path}")
    metadata, _, name = entries[0].partition(b"\t")
    mode, oid, stage = metadata.split()
    if stage != b"0" or mode not in ALLOWED_INDEX_MODES or name != path.encode("utf-8"):
        raise ValueError(f"expected a regular stage-0 WBS blob: {path}")
    return subprocess.check_output(["git", "cat-file", "blob", oid], cwd=root, timeout=10)


def module_of(path: str) -> str | None:
    if path.endswith(".java"):
        return next(
            (module for prefix, module in JAVA_ROOTS.items() if path.startswith(prefix)), None
        )
    return None


def tracked_java_paths(root: Path) -> dict[str, str]:
    command = ["git", "ls-files", "--stage", "-z", "--", *JAVA_ROOTS]
    entries = subprocess.check_output(command, cwd=root, timeout=10)
    paths = {}
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, _, raw_name = entry.partition(b"\t")
        name = raw_name.decode("utf-8")
        module = module_of(name)
        if module is None:
            continue
        mode, _, stage = metadata.split()
        if stage != b"0" or mode not in ALLOWED_INDEX_MODES or name in paths:
            raise ValueError(f"expected one regular stage-0 Java entry: {name}")
        paths[name] = module
    return paths


def validate_java_roster(root: Path, inventory: bytes) -> dict:
    artifacts = json.loads(inventory).get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("expected the WBS artifacts list")
    registered = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str):
            raise ValueError("expected a WBS artifact path")
        path = artifact["path"]
        module = module_of(path)
        if module is None:
            continue
        if path in registered:
            raise ValueError(f"duplicate Java registration: {path}")
        if artifact.get("module", module) != module:
            raise ValueError(f"incorrect Java module registration: {path}")
        for field in ("owner", "costOwner"):
            value = artifact.get(field)
            if not isinstance(value, str) or not value.startswith("WBS-") or len(value) <= 4:
                raise ValueError(f"missing Java {field}: {path}")
        registered.add(path)

    tracked = tracked_java_paths(root)
    missing = sorted(tracked.keys() - registered)
    obsolete = sorted(registered - tracked.keys())
    if missing or obsolete:
        raise ValueError(f"Java roster mismatch: missing={missing}, obsolete={obsolete}")
    by_module = dict.fromkeys(JAVA_ROOTS.values(), 0)
    for module in tracked.values():
        by_module[module] += 1
    return {"trackedJavaMain": len(tracked), "javaMainByModule": by_module}


def validate_index(root: Path, *, check_java_roster: bool = False) -> dict:
    inventory = read_index_blob(root, INVENTORY)
    result = _GUARD["validate_bytes"](
        inventory, read_index_blob(root, ACCEPTANCE)
    )
    if check_java_roster:
        result.update(validate_java_roster(root, inventory))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-java-roster",
        action="store_true",
        help="check the six current product Java directories against the staged artifact list",
    )
    args = parser.parse_args()
    try:
        print(json.dumps(validate_index(ROOT, check_java_roster=args.check_java_roster)))
        return 0
    except (ValueError, subprocess.SubprocessError) as ex:
        print(str(ex), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
