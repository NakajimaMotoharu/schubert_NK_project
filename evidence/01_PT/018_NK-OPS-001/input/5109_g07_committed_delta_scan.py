"""Scan an immutable committed delta without exporting candidate values."""
from datetime import datetime, timezone
import gzip
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
START = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/405_G07最近公開差分開始.json")
EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence/PG39196-g07-current-published-delta-v1")
WORK = ROOT.parent / "pgpt-runs/PG379/pg39196-g07-current-published-delta-v1"
SCANNER = ROOT.parent / "toolchain/gitleaks-8.30.1-linux-x64/gitleaks"
SOURCE_LIMIT = 32 * 1024**2
HELD = {
    "TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec",
    "WebStartupException", "RootFailedStartRecoveryTest", "RootFailedStartPairRecoveryTest",
    "SnapshotKeyCloseWitness", "pg9892_snapshot_key_close_witness",
}


def digest(content):
    return hashlib.sha256(content).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], timeout=45)


def write(path, value):
    with path.open("x", encoding="utf-8") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def committed_versions(parent, head):
    subprocess.run(["git", "merge-base", "--is-ancestor", parent, head], check=True, timeout=15)
    commits = git("rev-list", "--reverse", f"{parent}..{head}").decode().splitlines()
    versions = {}
    for commit in commits:
        changes = git("diff-tree", "--no-commit-id", "-r", "--raw", "-z", "--no-renames", commit)
        fields = changes.decode().rstrip("\0").split("\0") if changes else []
        for header, path in zip(fields[::2], fields[1::2], strict=True):
            mode = header.split()[1]
            oid = header.split()[3]
            if mode in ("100644", "100755"):
                assert path and not path.startswith("/") and ".." not in Path(path).parts
                versions.setdefault((path, oid), commit)
    return commits, versions


def projection(versions):
    rows = []
    for (path, oid), first in versions.items():
        relative = Path(path)
        if relative.stem.split("$")[0] in HELD:
            rows.append(dict(path=path, blobOid=oid, firstCommit=first, treatment="NAME_ONLY_HELD"))
            continue
        assert re.fullmatch(r"[0-9a-f]{40}", oid)
        size = int(git("cat-file", "-s", oid))
        assert size <= SOURCE_LIMIT, "oversize input requires its own reviewed scope"
        raw = git("cat-file", "blob", oid)
        assert len(raw) == size
        expanded = raw.startswith(b"\x1f\x8b")
        if expanded:
            with gzip.GzipFile(fileobj=BytesIO(raw)) as content:
                plain = content.read(SOURCE_LIMIT + 1)
            assert len(plain) <= SOURCE_LIMIT, "archive expansion limit"
        else:
            plain = raw
        try:
            assert b"\x00" not in plain
            plain.decode("utf-8")
            kind = "text"
        except (UnicodeDecodeError, AssertionError):
            kind = "binary"
        local = Path(kind) / f"{len(rows):06}" / (relative.stem if expanded else relative.name)
        target = WORK / local
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(plain)
        rows.append(dict(path=path, blobOid=oid, firstCommit=first, blobSha256=digest(raw),
                         decodedSha256=digest(plain), gzipExpanded=expanded,
                         relativeProjection=local.as_posix(), treatment=kind))
    return rows


def main():
    start = json.loads(START.read_bytes())
    before = start["values"]["fromCommit"]
    head = start["values"]["source"]
    assert git("rev-parse", "HEAD").decode().strip() == head
    assert git("rev-parse", "origin/dev-foundation").decode().strip() == head
    available = shutil.disk_usage(ROOT).free
    assert available >= 1300 * 1024**2
    commits, versions = committed_versions(before, head)
    assert len(commits) > 0 and len(versions) > 0 and len(versions) <= 3500
    assert not EVIDENCE.exists()
    EVIDENCE.mkdir()
    rows = projection(versions)
    p = WORK / "projection.json"
    write(p, rows)
    report = WORK / "scanner-redacted.json"
    text_dir = WORK / "text"
    command = [str(SCANNER), "dir", "--no-banner", "--no-color", "--redact=100",
               "--ignore-gitleaks-allow", "--gitleaks-ignore-path", str(text_dir),
               "--report-format=json", "--report-path", str(report), "--timeout", "75", str(text_dir)]
    started = now()
    scan = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    captured_at = now()
    assert scan.returncode in (0, 1) and report.is_file()
    findings = json.loads(report.read_bytes())
    assert (not findings) == (scan.returncode == 0)
    mapping = {str((WORK / r["relativeProjection"]).resolve()): r for r in rows if r["treatment"] == "text"}
    findings_meta = []
    for item in findings:
        path = Path(item["File"])
        row = mapping[str((WORK / path).resolve())]
        line = int(item["StartLine"])
        candidate = Path(WORK / row["relativeProjection"]).read_bytes().splitlines()[line - 1]
        findings_meta.append(dict(path=row["path"], blob=row["blobOid"], line=line,
                                  rule=item["RuleID"], lineSha256=digest(candidate)))
    results = dict(fromCommit=before, throughCommit=head, commits=len(commits),
                   trackedBlobVersions=len(rows), text=sum(r["treatment"] == "text" for r in rows),
                   binary=sum(r["treatment"] == "binary" for r in rows),
                   heldMetadataOnly=sum(r["treatment"] == "NAME_ONLY_HELD" for r in rows),
                   expandedGzip=sum(r.get("gzipExpanded", False) for r in rows),
                   findings=findings_meta, findingsCount=len(findings_meta), actualScannerExit=scan.returncode,
                   scannerCommand=command, scannerSha256=digest(SCANNER.read_bytes()),
                   projectionSha256=digest(p.read_bytes()), reportSha256=digest(report.read_bytes()),
                   reportPersistedInGit=False, untrackedRead=0, privateRuntimeFilesRead=0,
                   productTests=0, wholeG07Accepted=False, startedAtUTC=started, terminalAtUTC=captured_at)
    write(EVIDENCE / "scan-terminal.json", results)
    print({k: results[k] for k in ("commits", "text", "binary", "heldMetadataOnly", "findingsCount", "actualScannerExit")})


if __name__ == "__main__":
    sys.exit(main())
