"""Check public PGPT manifest path and SHA-256 references against fixed Git objects."""

import argparse
from collections import Counter
from functools import cache
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


COMMIT = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
PUBLIC_ROOTS = {"documents", "evidence", "program", "src", "tools"}
CURRENT_BASELINE = ("program", "characterization", "baseline", "current")


def git(repo, *arguments, required=True):
    return subprocess.run(
        ["git", "--no-replace-objects", "--literal-pathspecs", *arguments],
        cwd=repo,
        capture_output=True,
        check=required,
        timeout=45,
    )


def exact_source(value):
    return value if isinstance(value, str) and COMMIT.fullmatch(value) else None


def local_path(repo, value):
    path = PurePosixPath(value)
    if path.is_absolute():
        try:
            path = path.relative_to(repo)
        except ValueError:
            return None
    if (
        not path.parts
        or path.parts[0] not in PUBLIC_ROOTS
        or ".." in path.parts
        or "\0" in value
        or path.parts[:4] == CURRENT_BASELINE
    ):
        return None
    return path.as_posix()


def pins(value):
    if isinstance(value, dict):
        path, sha = value.get("path"), value.get("sha256")
        if isinstance(path, str) and isinstance(sha, str) and SHA256.fullmatch(sha):
            yield path, sha, exact_source(value.get("source"))
        for child in value.values():
            yield from pins(child)
    elif isinstance(value, list):
        for child in value:
            yield from pins(child)


def audit(repo, start, end):
    if not exact_source(start) or not exact_source(end):
        raise ValueError("expected two full Git commit IDs")
    git(repo, "merge-base", "--is-ancestor", start, end)
    span = f"{start}..{end}"
    changed = git(
        repo, "diff", "--name-only", "--diff-filter=AMR", "-z", span, "--", "evidence/01_PT"
    )
    paths = changed.stdout.decode("utf-8").split("\0")
    manifests = sorted(p for p in paths if PurePosixPath(p).name == "manifest.json")
    counts = Counter(current=0, historical=0, externalOrProtected=0)
    unresolved = []

    @cache
    def blob_hash(commit, path):
        result = git(repo, "cat-file", "blob", f"{commit}:{path}", required=False)
        return hashlib.sha256(result.stdout).hexdigest() if result.returncode == 0 else None

    @cache
    def path_history(path):
        return git(repo, "log", "--format=%H", span, "--", path).stdout.decode().splitlines()

    for manifest in manifests:
        content = json.loads(git(repo, "cat-file", "blob", f"{end}:{manifest}").stdout)
        parent_source = exact_source(content.get("source")) if isinstance(content, dict) else None
        references = set(pins(content))
        for raw_path, expected, source in sorted(
            references, key=lambda row: (row[0], row[1], row[2] or "")
        ):
            path = local_path(repo, raw_path)
            if path is None:
                counts["externalOrProtected"] += 1
                continue
            candidates = (source,) if source else (end, parent_source, start)
            actual = next(
                (c for c in dict.fromkeys(candidates) if c and blob_hash(c, path) == expected),
                None,
            )
            if actual is None and source is None:
                actual = next(
                    (c for c in path_history(path) if blob_hash(c, path) == expected),
                    None,
                )
            if actual is None:
                unresolved.append(
                    {"manifest": manifest, "path": path, "sha256": expected, "source": source}
                )
            else:
                counts["current" if actual == end else "historical"] += 1

    return {
        "rangeStart": start,
        "rangeEnd": end,
        "manifests": len(manifests),
        **counts,
        "unresolved": unresolved,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()
    try:
        repo = Path(git(args.repo.resolve(), "rev-parse", "--show-toplevel").stdout.decode().strip())
        result = audit(repo, args.start, args.end)
    except (ValueError, OSError, subprocess.SubprocessError) as failure:
        # Failure diagnostics expose structure only. Git command stderr can describe private data.
        parser.exit(2, f"published pin verification failed ({type(failure).__name__})\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
