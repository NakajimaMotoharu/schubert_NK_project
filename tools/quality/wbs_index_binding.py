"""Validate the WBS inventory reference in the Git index before publication."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
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
RESOURCE_ROOTS = {
    prefix.removesuffix("java/") + "resources/": module
    for prefix, module in JAVA_ROOTS.items()
} | {"src/deployment/": "deployment"}


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


def resource_group(path: str) -> str | None:
    return next(
        (group for prefix, group in RESOURCE_ROOTS.items() if path.startswith(prefix)), None
    )


def tracked_paths(root: Path, roots, group_of, entry_kind: str) -> dict[str, str]:
    command = ["git", "ls-files", "--stage", "-z", "--", *roots]
    entries = subprocess.check_output(command, cwd=root, timeout=10)
    paths = {}
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, _, raw_name = entry.partition(b"\t")
        name = raw_name.decode("utf-8")
        group = group_of(name)
        if group is None:
            continue
        mode, _, stage = metadata.split()
        if stage != b"0" or mode not in ALLOWED_INDEX_MODES or name in paths:
            raise ValueError(f"expected one regular stage-0 {entry_kind} entry: {name}")
        paths[name] = group
    return paths


def require_owner(artifact: dict, group: str) -> None:
    for field in ("owner", "costOwner"):
        value = artifact.get(field)
        if not isinstance(value, str) or not value.startswith("WBS-") or len(value) <= 4:
            raise ValueError(f"missing {group} {field}: {artifact['path']}")


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
        require_owner(artifact, "Java")
        registered.add(path)

    tracked = tracked_paths(root, JAVA_ROOTS, module_of, "Java")
    missing = sorted(tracked.keys() - registered)
    obsolete = sorted(registered - tracked.keys())
    if missing or obsolete:
        raise ValueError(f"Java roster mismatch: missing={missing}, obsolete={obsolete}")
    by_module = dict.fromkeys(JAVA_ROOTS.values(), 0)
    for module in tracked.values():
        by_module[module] += 1
    return {"trackedJavaMain": len(tracked), "javaMainByModule": by_module}


def verify_resource_retirement(root: Path, path: str, commit: str) -> None:
    if not re.fullmatch("[0-9a-f]{40}", commit):
        raise ValueError(f"invalid resource retirement commit: {path}")
    obj = subprocess.check_output(["git", "cat-file", "-t", commit], cwd=root, timeout=10)
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=root, timeout=10,
        check=False, capture_output=True,
    )
    if obj != b"commit\n" or ancestor.returncode != 0:
        raise ValueError(f"retirement commit is outside branch history: {path}")
    deleted = subprocess.check_output(
        ["git", "diff-tree", "--no-commit-id", "-r", "-z", "--name-only",
         "--diff-filter=D", commit, "--", ":(literal)" + path], cwd=root, timeout=10,
    )
    if deleted != path.encode("utf-8") + b"\0":
        raise ValueError(f"retirement commit did not delete the resource: {path}")


def validate_resource_roster(root: Path, inventory: bytes) -> dict:
    value = json.loads(inventory)
    registered = set()
    for artifact in value["artifacts"]:
        path = artifact["path"]
        if resource_group(path) is None:
            continue
        if path in registered:
            raise ValueError(f"duplicate resource registration: {path}")
        require_owner(artifact, "resource")
        registered.add(path)

    tracked = tracked_paths(root, RESOURCE_ROOTS, resource_group, "resource")
    retired = set()
    proofs = value.get("retiredProductResources", [])
    if not isinstance(proofs, list):
        raise ValueError("expected a product resource retirement list")
    for proof in proofs:
        if not isinstance(proof, dict) or set(proof) != {"path", "removedBy"}:
            raise ValueError("expected a product resource retirement proof")
        path, commit = proof["path"], proof["removedBy"]
        if (not isinstance(path, str) or not isinstance(commit, str)
                or str(PurePosixPath(path)) != path or ".." in PurePosixPath(path).parts
                or "\\" in path or path not in registered or path in tracked or path in retired):
            raise ValueError(f"invalid retired product resource: {path}")
        verify_resource_retirement(root, path, commit)
        retired.add(path)
    missing = sorted(tracked.keys() - registered)
    obsolete = sorted(registered - tracked.keys() - retired)
    if missing or obsolete:
        raise ValueError(f"resource roster mismatch: missing={missing}, obsolete={obsolete}")
    counts = dict.fromkeys(RESOURCE_ROOTS.values(), 0)
    for group in tracked.values():
        counts[group] += 1
    return {
        "trackedProductResources": len(tracked), "productResourcesByGroup": counts,
        "retiredProductResources": len(retired),
    }


def validate_index(
    root: Path, *, check_java_roster: bool = False, check_product_roster: bool = False
) -> dict:
    inventory = read_index_blob(root, INVENTORY)
    result = _GUARD["validate_bytes"](
        inventory, read_index_blob(root, ACCEPTANCE)
    )
    if check_java_roster or check_product_roster:
        result.update(validate_java_roster(root, inventory))
    if check_product_roster:
        result.update(validate_resource_roster(root, inventory))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-java-roster",
        action="store_true",
        help="check the six current product Java directories against the staged artifact list",
    )
    parser.add_argument(
        "--check-product-roster", action="store_true",
        help="check staged Java Main, resources and deployment paths and declared retirements",
    )
    args = parser.parse_args()
    try:
        print(json.dumps(validate_index(
            ROOT, check_java_roster=args.check_java_roster,
            check_product_roster=args.check_product_roster,
        )))
        return 0
    except (ValueError, subprocess.SubprocessError) as ex:
        print(str(ex), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
