"""Check public PGPT manifest pins against Git commits or a staged snapshot."""

import argparse
from collections import Counter
from functools import cache
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from static_input_scope import invalid_constant, unique_object


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
        if "path" in value and "sha256" in value and (path is not None or sha is not None):
            digest = sha if isinstance(sha, str) and SHA256.fullmatch(sha) else None
            explicit_path = path if isinstance(path, str) and path.strip() else None
            yield explicit_path, digest, exact_source(value.get("source")), "source" in value
        for child in value.values():
            yield from pins(child)
    elif isinstance(value, list):
        for child in value:
            yield from pins(child)


def audit(repo, start, end, *, staged=False):
    if not exact_source(start) or not exact_source(end):
        raise ValueError("expected two full Git commit IDs")

    @cache
    def is_commit(candidate):
        result = git(
            repo,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{candidate}^{{commit}}",
            required=False,
        )
        return result.returncode == 0 and result.stdout.strip() == candidate.encode()

    if not is_commit(start) or not is_commit(end):
        raise ValueError("range must identify Git commits")
    git(repo, "merge-base", "--is-ancestor", start, end)
    span = f"{start}..{end}"
    staged_tree = git(repo, "write-tree").stdout.decode().strip() if staged else None
    current = staged_tree or end
    comparison = (start, staged_tree) if staged_tree else (span,)
    changed = git(
        repo, "diff", "--name-only", "--diff-filter=AMR", "-z", *comparison, "--", "evidence/01_PT"
    )
    paths = changed.stdout.decode("utf-8").split("\0")
    manifests = sorted(p for p in paths if PurePosixPath(p).name == "manifest.json")
    counts = Counter(current=0, historical=0, externalOrProtected=0)
    unresolved = []

    @cache
    def blob_hash(revision, path):
        if revision != staged_tree and not is_commit(revision):
            return None
        result = git(repo, "cat-file", "blob", f"{revision}:{path}", required=False)
        return hashlib.sha256(result.stdout).hexdigest() if result.returncode == 0 else None

    @cache
    def path_history(path):
        return git(repo, "log", "--format=%H", span, "--", path).stdout.decode().splitlines()

    for manifest in manifests:
        content = json.loads(
            git(repo, "cat-file", "blob", f"{current}:{manifest}").stdout,
            object_pairs_hook=unique_object,
            parse_constant=invalid_constant,
        )
        parent_source = exact_source(content.get("source")) if isinstance(content, dict) else None
        references = set(pins(content))
        for raw_path, expected, source, has_explicit_source in sorted(
            references, key=lambda row: (row[0] or "", row[1] or "", row[2] or "", row[3])
        ):
            if raw_path is None:
                unresolved.append(
                    {
                        "manifest": manifest,
                        "path": None,
                        "sha256": expected,
                        "source": source,
                        "reason": "INVALID_EXPLICIT_PATH",
                    }
                )
                continue
            path = local_path(repo, raw_path)
            if path is None:
                counts["externalOrProtected"] += 1
                continue
            if expected is None:
                unresolved.append(
                    {
                        "manifest": manifest,
                        "path": path,
                        "sha256": None,
                        "source": source,
                        "reason": "INVALID_EXPLICIT_SHA256",
                    }
                )
                continue
            if has_explicit_source and (source is None or not is_commit(source)):
                unresolved.append(
                    {
                        "manifest": manifest,
                        "path": path,
                        "sha256": expected,
                        "source": None,
                        "reason": "INVALID_EXPLICIT_SOURCE",
                    }
                )
                continue
            candidates = (source,) if source else (current, parent_source, start)
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
                counts["current" if actual == current else "historical"] += 1

    result = {
        "rangeStart": start,
        "rangeEnd": end,
        "manifests": len(manifests),
        **counts,
        "unresolved": unresolved,
    }
    if staged_tree:
        result["stagedTree"] = staged_tree
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--start", required=True)
    endpoint = parser.add_mutually_exclusive_group(required=True)
    endpoint.add_argument("--end")
    endpoint.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    try:
        repo = Path(git(args.repo.resolve(), "rev-parse", "--show-toplevel").stdout.decode().strip())
        head = git(repo, "rev-parse", "HEAD").stdout.decode().strip() if args.staged else args.end
        result = audit(repo, args.start, head, staged=args.staged)
    except (ValueError, OSError, subprocess.SubprocessError) as failure:
        # Failure diagnostics expose structure only. Git command stderr can describe private data.
        parser.exit(2, f"published pin verification failed ({type(failure).__name__})\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
