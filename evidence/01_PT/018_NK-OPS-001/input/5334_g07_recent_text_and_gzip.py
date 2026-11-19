"""Scan one newly published Git range without reading retained private logs."""

from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PLAN = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
MAX_LOG = 2 * 1024**2
MAX_BATCH = 32 * 1024**2


def hash_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    p = Path(path)
    return dict(path=str(p), sha256=hash_bytes(p.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args], timeout=60)


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    start = read(next(PLAN.glob("782_*")))
    work = start["values"]
    assert all(pin(ref["path"]) == ref for ref in work["oracleReferences"])
    old = read(work["oracleReferences"][1]["path"])
    old_compressed = read(work["oracleReferences"][2]["path"])
    first, last = old["source"], work["source"]
    counts = {}
    for row in git("diff", "--no-renames", "--numstat", "-z", first, last).split(b"\0"):
        if row:
            additions, deletions, name = row.decode().split("\t", 2)
            counts[name] = (additions, deletions)
    excluded = {}
    for meta in work["oracleReferences"][3:]:
        disposition = read(meta["path"])
        name = disposition.get("allSignalsFile", disposition.get("sourceHashFile"))
        data = git("show", f"{last}:{name}")
        assert hash_bytes(data) == disposition["compiledClassMapSha256"]
        assert disposition["signals"] == 18 and disposition["candidateSecretsInClassMap"] == 0
        excluded[name] = meta
    text, compressed, other = [], [], []
    old_names = set(git("ls-tree", "-r", "-z", "--name-only", first, "--", str(OPS)).decode().split("\0"))
    for path, delta in sorted(counts.items()):
        if path in excluded:
            continue
        if path.endswith(".gz") and path.startswith(str(OPS) + "/") and path not in old_names:
            compressed.append(path)
        elif path.endswith((".exec", ".gz")) or delta == ("-", "-"):
            other.append(path)
        else:
            text.append(path)
    assert set(text).isdisjoint(compressed) and set(text).isdisjoint(excluded)
    patch_args = ["diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--text",
                  first, last, "--", *text]
    patch = git(*patch_args)
    all_logs = io.BytesIO()
    logs = []
    for path in compressed:
        blob = git("show", f"{last}:{path}")
        with gzip.GzipFile(fileobj=io.BytesIO(blob)) as stream:
            data = stream.read(MAX_LOG + 1)
        assert len(data) <= MAX_LOG and all_logs.tell() + len(data) <= MAX_BATCH
        data.decode("utf-8", "strict")
        all_logs.write(data)
        all_logs.write(b"\n")
        logs.append(dict(path=path, compressedSha256=hash_bytes(blob),
                         decodedBytes=len(data), decodedSha256=hash_bytes(data)))

    scanner = Path.cwd().parent / "toolchain/gitleaks-8.30.1-linux-x64/gitleaks"
    assert scanner.is_file() and scanner.resolve() == scanner
    scanner_status = {}
    payloads = {"netTextPatch": patch, "publishedGzipText": all_logs.getvalue()}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-g07-redacted-") as tmp:
        for label, data in payloads.items():
            report = Path(tmp) / (label + ".json")
            cmd = [scanner, "stdin", "--redact", "--no-banner", "--no-color",
                   "--report-format=json", "--report-path", report]
            outcome = subprocess.run(cmd, input=data, capture_output=True, timeout=90, check=False)
            rows = read(report) if report.exists() else []
            scanner_status[label] = dict(exit=outcome.returncode, bytes=len(data), sha256=hash_bytes(data),
                                         signals=len(rows), ruleCounts=dict(Counter(row["RuleID"] for row in rows)))
    accepted_scope = all(scope["exit"] == 0 and scope["signals"] == 0 for scope in scanner_status.values())
    result = dict(actualExit=0 if accepted_scope else 1, source=last, productionCore=work["productionCoreMain"],
                  previousCursor=first, startEvent=start["eventId"],
                  commits=int(git("rev-list", "--count", f"{first}..{last}").strip()),
                  patchPaths=len(text), gzipPaths=len(logs), encodedLogEvidence=logs,
                  otherBinaryMetadataOnly=other, checksumOnlyMaps=excluded,
                  priorCompressedScopeNotReplayed=bool(old_compressed["source"]),
                  scanner=pin(scanner), scan=scanner_status, matchingRawValuesSaved=0,
                  firstPassNoSignals=accepted_scope, wholeG07Accepted=False, whole451Accepted=False,
                  productTests=0, newFormalAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = OPS / work["run"]
    out.mkdir()
    path = out / "manifest.json"
    with path.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(path), len(text), len(logs), len(other), scanner_status)
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
