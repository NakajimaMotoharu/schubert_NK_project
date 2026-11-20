"""Sweep only the published textual patch interval after the prior scan cursor."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess


def sha(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args], timeout=35)


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
start = json.loads(next(plan.glob("1322_*")).read_bytes())
values = start["values"]
core, head = values["productionCoreMain"], values["source"]
assert git("rev-parse", "HEAD", "origin/dev-foundation").decode().splitlines() == [head, head]
assert all(pin(Path(row["path"])) == row for row in values["oracleReferences"])
last = Path(values["oracleReferences"][1]["path"])
prior = json.loads(last.read_bytes())
assert prior["actualExit"] == prior["detected"] == 0
base = prior["src"]
assert git("merge-base", base, head).decode().strip() == base
commits = git("rev-list", "--reverse", f"{base}..{head}").decode().splitlines()
assert commits

published = ("documents/", "src/", "evidence/01_PT/", "tools/quality/")
suffixes = {".md", ".java", ".py", ".json", ".xml", ".tsv", ".txt", ".patch"}
paths = set()
patches = []
lineage = []
for commit in commits:
    names = git("diff", "--name-only", "-z", commit + "^", commit).decode().split("\0")[:-1]
    assert names and all(name.startswith(published) and Path(name).suffix in suffixes for name in names)
    assert not any(name.endswith((".safe.json", ".raw.txt")) for name in names)
    patch = git("diff", "--no-ext-diff", "--no-renames", "--unified=0", commit + "^", commit)
    assert b"GIT binary patch" not in patch and b"Binary files " not in patch
    paths.update(names)
    patches.append(patch)
    lineage.append(dict(commit=commit, pathCount=len(names), patchSha256=sha(patch)))
assert all(not path.startswith("program/characterization/baseline/") for path in paths)
protected = "program/characterization/baseline/current"
baseline_before = git("rev-parse", f"{base}:{protected}").decode().strip()
assert git("rev-parse", f"{head}:{protected}").decode().strip() == baseline_before
scanner = Path("../toolchain/gitleaks-8.30.1-linux-x64/gitleaks")
command = [str(scanner), "stdin", "--redact=100", "--no-banner"]
combined = b"\n".join(patches)
check = subprocess.run(command, input=combined, capture_output=True, timeout=60)
out = Path("evidence/01_PT/018_NK-OPS-001/evidence") / values["run"]
out.mkdir()
data = dict(actualExit=check.returncode, detected=0 if check.returncode == 0 else None,
            source=core, baseExclusive=base, headInclusive=head, priorScan=pin(last),
            startedBy=start["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
            commits=len(commits), uniquePaths=len(paths), perCommit=lineage,
            patchStreamSha256=sha(combined), baselineTree=baseline_before, scanner=pin(scanner),
            command=command, rawScannerOutputPublished=False, protectedPathContentsRead=0,
            untrackedPathsRead=0, productTests=0, fullRepositoryScope=False, whole451=False, formalDelta=0)
path = out / "manifest.json"
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(check.returncode, len(commits), len(paths), pin(path))
raise SystemExit(check.returncode)
