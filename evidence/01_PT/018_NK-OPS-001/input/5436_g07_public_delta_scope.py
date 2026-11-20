"""Scan only reviewed public Git deltas from the stated execution range."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[4]
PLAN = next((ROOT / "documents/400_PGPT/470_PMO").glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
TOOL = ROOT.parent / "toolchain/gitleaks-8.30.1-linux-x64/gitleaks"
BASE = "ae02f5e5dce5ea5af6c533715c5db84a586948e2"
HOLD = tuple(f"evidence/01_PT/018_NK-OPS-001/evidence/{scope}*"
             for scope in ("PG40750-", "PG40766-"))


def sha(data):
    return sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=22)


def main():
    start = json.loads(next(PLAN.glob("1138_G07限定*")).read_bytes())
    task = start["values"]
    assert all(sha(Path(ref["path"]).read_bytes()) == ref["sha256"]
               for ref in task["oracleReferences"])
    head = git("rev-parse", "HEAD").decode().strip()
    assert head == task["source"] == git("rev-parse", "origin/dev-foundation").decode().strip()
    assert git("merge-base", BASE, head).decode().strip() == BASE
    commits = git("rev-list", "--reverse", f"{BASE}..{head}").decode().splitlines()
    parts = []
    files = set()
    exclusions = set()
    patch_bytes = []
    for commit in commits:
        paths = git("diff", "--name-only", "-z", commit+"^", commit).decode().split("\0")[:-1]
        current_paths = [p for p in paths if Path(p).suffix == ".gz"
                         or "/PG40750-" in p or "/PG40766-" in p]
        assert all("/PG40750-" in p or "/PG40766-" in p for p in current_paths)
        allowed = set(paths) - set(current_paths)
        assert all(Path(name).suffix in {".json", ".md", ".py", ".java", ".tsv",
                                        ".txt", ".xml", ".stdout", ".stderr"}
                   for name in allowed)
        blob = git("diff", "--no-ext-diff", "--no-renames", "--unified=0", commit+"^", commit,
                   "--", *(f":(exclude){p}" for p in sorted(HOLD)))
        files.update(allowed)
        exclusions.update(current_paths)
        parts.append({"commit": commit, "patchSha256": sha(blob), "allowedPaths": len(allowed)})
        patch_bytes.append(blob)
    total = b"\n".join(patch_bytes)
    cli = [str(TOOL), "stdin", "--redact=100", "--no-banner"]
    run = subprocess.run(cli, input=total, capture_output=True, timeout=45)
    assert run.returncode in (0, 1)
    result = dict(
        actualExit=run.returncode, tool=sha(TOOL.read_bytes()), command=cli,
        aggregateInputSha256=sha(total), terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        source=head, baseExclusive=BASE, startEvent=start["eventId"], commits=parts,
        approvedTextPaths=len(files), excludedQuarantinedPaths=sorted(exclusions),
        findings=0 if run.returncode == 0 else None, rawToolOutputSaved=False,
        currentFullRepositoryScanned=False, wholeG07=False, whole451=False, newFormalAcceptance=0,
    )
    out = OPS / task["run"]
    out.mkdir()
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print({"exit": run.returncode, "commits": len(commits),
           "allowedPaths": len(files), "quarantinedPaths": len(exclusions)})
    return run.returncode


if __name__ == "__main__":
    raise SystemExit(main())
