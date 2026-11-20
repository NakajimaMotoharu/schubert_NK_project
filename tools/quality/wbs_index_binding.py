"""Validate the WBS inventory reference in the Git index before publication."""

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


def validate_index(root: Path) -> dict:
    return _GUARD["validate_bytes"](
        read_index_blob(root, INVENTORY),
        read_index_blob(root, ACCEPTANCE),
    )


def main() -> int:
    try:
        print(json.dumps(validate_index(ROOT)))
        return 0
    except (ValueError, subprocess.SubprocessError) as ex:
        print(str(ex), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
