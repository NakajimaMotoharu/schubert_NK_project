"""Archive and verify the two exact owned G07 duplicate text projections."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tarfile

EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
RUNS = Path.cwd().parent / "pgpt-runs/PG379"
OUT = EVIDENCE / "PG39286-g07-reversible-projection-retention-v1"
REVIEWED = (
    ("PG39196-g07-current-published-delta-v1", "final-manifest.json", 1292),
    ("PG39284-g07-published-recorder-delta-v1", "terminal-manifest.json", 640),
)


def sha(stream):
    return hashlib.file_digest(stream, "sha256").hexdigest()


def hash_file(path):
    with path.open("rb") as f:
        return sha(f)


def load(path):
    return json.loads(path.read_bytes())


def write(path, data):
    with path.open("x") as f:
        f.write(json.dumps(data, indent=2) + "\n")
        f.flush()
        os.fsync(f.fileno())


def verify_member_inventory(archive, expected):
    seen = set()
    with tarfile.open(archive, "r|gz") as contents:
        for member in contents:
            assert member.isreg() and member.name not in seen
            row = expected[member.name]
            assert row["bytes"] == member.size
            with contents.extractfile(member) as item:
                assert sha(item) == row["sha256"]
            seen.add(member.name)
    assert seen == set(expected)


def preserve(name, final_name, count):
    public = EVIDENCE / name
    work = RUNS / name.lower()
    assert work.is_dir() and work.resolve() == work and work.stat().st_uid == os.getuid()
    before = shutil.disk_usage(work).free
    proof = load(public / final_name)
    scan_path = public / "scan-terminal.json"
    scan = load(scan_path)
    assert proof["unresolvedCandidates"] == proof["unqualifiedBinary"] == proof["confirmedSecrets"] == 0
    assert proof["scan"] == {"path": str(scan_path), "sha256": hash_file(scan_path)}
    index = work / "projection.json"
    report = work / "scanner-redacted.json"
    assert hash_file(index) == scan["projectionSha256"]
    assert hash_file(report) == scan["reportSha256"]
    expected = {}
    for row in load(index):
        if row["treatment"] != "text":
            continue
        rel = Path(row["relativeProjection"])
        assert len(rel.parts) == 3 and rel.parts[0] == "text" and len(rel.parts[1]) == 6 and rel.parts[1].isdigit()
        path = work / rel
        info = path.lstat()
        assert path.resolve() == path and stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1
        assert hash_file(path) == row["decodedSha256"]
        assert str(rel) not in expected
        expected[str(rel)] = dict(bytes=info.st_size, sha256=row["decodedSha256"])
    assert len(expected) == scan["text"] == count
    assert all(p.is_dir() for p in set((work / rel).parent for rel in expected))
    declared = {str(p.relative_to(work)) for p in (work / "text").glob("*/*")}
    assert declared == expected.keys(), "other input in projection namespace"
    archive = work / "text-projection-retained.tar.gz"
    with archive.open("xb") as dest:
        os.fchmod(dest.fileno(), 0o600)
        with tarfile.open(fileobj=dest, mode="w:gz", compresslevel=6) as packed:
            for rel in sorted(expected):
                packed.add(work / rel, arcname=rel, recursive=False)
        dest.flush()
        os.fsync(dest.fileno())
    verify_member_inventory(archive, expected)
    a_sha = hash_file(archive)
    receipt = work / "text-projection-retained.json"
    data = dict(actualExit=0, archive=str(archive), archiveSha256=a_sha, archiveBytes=archive.stat().st_size,
                files=count, uncompressedBytes=sum(v["bytes"] for v in expected.values()),
                decodedIndexSha256=scan["projectionSha256"], redactedReportSha256=scan["reportSha256"],
                restoreCommand=["tar", "-xzf", str(archive), "--no-same-owner", "-C", str(work)],
                sourceEvidence=str(public / final_name), sourceEvidenceSha256=hash_file(public / final_name),
                everyMemberVerified=True, gitOriginalAndScannerReportPreserved=True)
    write(receipt, data)
    assert hash_file(archive) == a_sha
    for rel, row in expected.items():
        path = work / rel
        assert path.resolve() == path and hash_file(path) == row["sha256"]
        path.unlink()
    assert not list((work / "text").glob("*/*"))
    assert hash_file(index) == scan["projectionSha256"]
    assert hash_file(report) == scan["reportSha256"]
    after = shutil.disk_usage(work).free
    return dict(data, receipt=str(receipt), receiptSha256=hash_file(receipt),
                availableBefore=before, availableAfter=after, duplicateTextCopiesReleased=count)


def main():
    OUT.mkdir()
    started = datetime.now(timezone.utc).isoformat()
    result = []
    for name, manifest, count in REVIEWED:
        result.append(preserve(name, manifest, count))
        write(OUT / f"{name}-receipt.json", result[-1])
    finish = datetime.now(timezone.utc).isoformat()
    summary = dict(actualExit=0, startedAtUTC=started, terminalAtUTC=finish,
                   availableBefore=result[0]["availableBefore"], availableAfter=result[-1]["availableAfter"],
                   duplicateTextCopiesReleased=sum(r["files"] for r in result),
                   originalPlainBytes=sum(r["uncompressedBytes"] for r in result),
                   retainedArchiveBytes=sum(r["archiveBytes"] for r in result), entries=result,
                   productTests=0, sameEvidenceReexecuted=False, externalOrProtectedActions=0)
    write(OUT / "manifest.json", summary)
    print({k: summary[k] for k in ("actualExit", "availableBefore", "availableAfter", "duplicateTextCopiesReleased", "retainedArchiveBytes")})


if __name__ == "__main__":
    main()
