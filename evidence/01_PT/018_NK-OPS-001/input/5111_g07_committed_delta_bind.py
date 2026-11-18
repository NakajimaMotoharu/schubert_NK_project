"""Independently bind Gitleaks coordinates to actual Git or approved byte identities."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
OUT = BASE / "PG39196-g07-current-published-delta-v1"
RUNS = Path.cwd().parent / "pgpt-runs/PG379"
WORK = RUNS / "pg39196-g07-current-published-delta-v1"
BUILD_WORK = {RUNS / n for n in ("pg38952-four-jdbc-candidate-build-v1",
                                  "pg39122-four-backup-candidate-build-v1")}
HELD = {"TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec",
        "WebStartupException", "RootFailedStartRecoveryTest", "RootFailedStartPairRecoveryTest"}
MODULES = ("protocol", "storage", "bootstrap", "batch")
TOKEN = re.compile(r"(?<![0-9a-f])(?:[0-9a-f]{40}|[0-9a-f]{64})(?![0-9a-f])")
FIELD = re.compile(r'\s*"([^"]+)"\s*:\s*"([0-9a-f]{40,64})"\s*,?')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, value):
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")


def git(*args):
    return subprocess.check_output(["git", *args], timeout=90)


def source_ground(path, token, manifest, head):
    if path.parts[0] != "src" or path.suffix not in {".java", ".template"}:
        return None
    assert not path.is_absolute() and ".." not in path.parts and path.stem not in HELD
    for label in ("sourceCore", "productionCoreMain", "source"):
        rev = manifest.get(label)
        if not isinstance(rev, str) or not re.fullmatch(r"[0-9a-f]{40}", rev):
            continue
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", rev, head],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        if ancestor.returncode == 0 and sha(git("show", f"{rev}:{path}")) == token:
            return dict(kind="tracked source content at the declared commit", path=str(path), revision=rev)
    return None


def class_ground(path, token, manifest):
    if path.parts[0] != "dev" or path.suffix != ".class" or path.stem.split("$")[0] in HELD:
        return None
    assert not path.is_absolute() and ".." not in path.parts
    work = Path(manifest.get("cwd", "."))
    if work not in BUILD_WORK:
        return None
    for module in MODULES:
        physical = work / f"src/schubert-nk-{module}/target/classes" / path
        if physical.is_file() and not physical.is_symlink():
            if physical.resolve() == physical and sha(physical.read_bytes()) == token:
                return dict(kind="exact four-module compiled bytes", module=module,
                            classPath=str(path), revision=manifest["sourceCore"])
    return None


def main():
    scan = load(OUT / "scan-terminal.json")
    head = scan["throughCommit"]
    prior = load(OUT / "adjudication-first.json")
    binary = load(OUT / "binary-qualification.json")
    raws = load(WORK / "scanner-redacted.json")
    assert ref(WORK / "scanner-redacted.json")["sha256"] == scan["reportSha256"]
    rows = load(WORK / "projection.json")
    assert ref(WORK / "projection.json")["sha256"] == scan["projectionSha256"]
    by_blob = {(r["path"], r["blobOid"]): r for r in rows}
    final = []
    categories = Counter()
    for index, (raw, row) in enumerate(zip(raws, prior, strict=True)):
        r = by_blob[row["path"], row["blob"]]
        local = WORK / r["relativeProjection"]
        line = local.read_bytes().splitlines()[row["line"] - 1]
        assert sha(line) == row["lineSha256"]
        assert raw["StartLine"] == row["line"] and raw["RuleID"] == row["rule"]
        a, z = raw["StartColumn"], raw["EndColumn"]
        text = line.decode()
        matches = [m[0] for m in TOKEN.finditer(text)
                   if max(0, min(m.end(), z + 1) - max(m.start(), a - 2)) >= len(m[0]) - 1]
        old = row["ground"]
        if old and old["kind"] == "exact previous adjudicated public line":
            decision = old
        elif old and len(matches) == 1:
            decision = old
        else:
            decision = None
            match = FIELD.fullmatch(text)
            if match and len(matches) == 1 and match[2] == matches[0]:
                path = Path(match[1])
                manifest = load(local)
                decision = source_ground(path, match[2], manifest, head) or class_ground(path, match[2], manifest)
        if decision:
            categories[decision["kind"]] += 1
        final.append(dict(row, ground=decision, findingIndex=index + 1, startColumn=a, endColumn=z))
    counts = dict(categories)
    pending = [r for r in final if r["ground"] is None]
    pending_binary = [x for x in binary if x.get("actualExit") != 0]
    write(OUT / "classified-findings.json", final)
    write(OUT / "unclassified-findings.json", pending)
    result = dict(actualExit=0, source=head, fromCommit=scan["fromCommit"], throughCommit=head,
                  commits=scan["commits"], trackedBlobVersions=scan["trackedBlobVersions"], text=scan["text"],
                  binary=scan["binary"], expandedGzip=scan["expandedGzip"], heldMetadataOnly=scan["heldMetadataOnly"],
                  actualScannerExit=scan["actualScannerExit"], categories=counts,
                  unresolvedCandidates=len(pending), unqualifiedBinary=len(pending_binary),
                  newUnresolvedOrConfirmedValueExported=False, confirmedSecrets=None if pending else 0,
                  scan=ref(OUT / "scan-terminal.json"), findings=ref(OUT / "classified-findings.json"),
                  binaryProof=ref(OUT / "binary-qualification.json"), unclassified=ref(OUT / "unclassified-findings.json"),
                  oldSourceResultsTransferred=False, productTests=0, wholeG07Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(OUT / "manifest.json", result)
    print(dict(counts=counts, unresolved=len(pending), unqualifiedBinary=len(pending_binary)))


if __name__ == "__main__":
    main()
