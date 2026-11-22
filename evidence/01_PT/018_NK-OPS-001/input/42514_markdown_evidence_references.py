"""Verify Markdown evidence bytes or an explicitly recorded Git revision."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def verify(root: Path, reference: dict) -> None:
    path = Path(reference["path"])
    digest = reference["sha256"]
    revision = reference.get("revision")
    if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
        raise ValueError("expected a repository-relative Markdown path")
    if not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("expected a lowercase SHA256 digest")
    full_path = root / path
    if revision is None:
        if full_path.is_symlink() or not full_path.resolve().is_relative_to(root):
            raise ValueError("expected an in-repository file")
        source = full_path.read_bytes()
    else:
        if not re.fullmatch(r"[a-f0-9]{40}", revision):
            raise ValueError("expected a full Git commit ID")
        source = subprocess.check_output(
            ["git", "show", f"{revision}:{path.as_posix()}"], cwd=root, timeout=10
        )
    if hashlib.sha256(source).hexdigest() != digest:
        raise ValueError(f"Markdown evidence digest mismatch: {path}")


def main() -> int:
    root = Path.cwd().resolve()
    references = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["references"]
    for reference in references:
        verify(root, reference)
    print(json.dumps({"verifiedReferences": len(references)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
