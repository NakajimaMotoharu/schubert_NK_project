"""Scan new public Git patches after the last scanner's exact good cursor."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess


def git(*args):
    return subprocess.check_output(["git", *args], timeout=30)


ops = Path("evidence/01_PT/018_NK-OPS-001/evidence")
plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
start = json.loads(next(plan.glob("1220_*")).read_bytes())
previous = json.loads(next(ops.glob("PG40806-*/manifest.json")).read_bytes())
base = previous["source"]
head = start["values"]["source"]
assert git("rev-parse", "origin/dev-foundation").decode().strip() == head
assert previous["actualExit"] == 0 and git("merge-base", base, head).decode().strip() == base
commits = git("rev-list", "--reverse", f"{base}..{head}").decode().splitlines()
paths, parts, records = set(), [], []
for revision in commits:
    changed = set(git("diff","--name-only","-z",f"{revision}^",revision).decode().split("\0")[:-1])
    assert changed and all("/PG40750-" not in p and "/PG40766-" not in p for p in changed)
    assert all(Path(name).suffix in {".json",".md",".py",".java",".xml"} for name in changed)
    patch = git("diff","--no-ext-diff","--no-renames","--unified=0",f"{revision}^",revision)
    records.append(dict(commit=revision,paths=len(changed),sha256=sha256(patch).hexdigest()))
    parts.append(patch)
    paths.update(changed)
scanner = Path("../toolchain/gitleaks-8.30.1-linux-x64/gitleaks")
assert sha256(scanner.read_bytes()).hexdigest() == previous["toolSha256"]
stream = b"\n".join(parts)
cli = [str(scanner),"stdin","--redact=100","--no-banner","--report-format","json","--report-path","/dev/stdout"]
scan = subprocess.run(cli,input=stream,capture_output=True,timeout=45)
result = dict(actualExit=scan.returncode,baseExclusive=base,source=head,productionCore=start["values"]["productionCoreMain"],
    aggregateSha256=sha256(stream).hexdigest(),patchRecords=records,commitCount=len(records),pathCount=len(paths),
    detected=0 if scan.returncode==0 else None,heldInputsOpened=0,externalActions=0,
    command=cli,rawToolOutputStored=False,wholeG07=False,whole451=False,formalDelta=0,
    terminalAtUTC=datetime.now(timezone.utc).isoformat())
out = ops/start["values"]["run"]/"manifest.json"
out.parent.mkdir()
out.write_text(json.dumps(result,indent=2)+"\n")
print(scan.returncode,len(records),len(paths),sha256(out.read_bytes()).hexdigest())
raise SystemExit(scan.returncode)
