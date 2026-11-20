"""Inspect every newly committed version of the bounded public Git interval."""

from collections import Counter
import gzip
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("5334_g07_recent_text_and_gzip.py")))
OPS, PLAN, git, pin, read, digest = (H[k] for k in ("OPS", "PLAN", "git", "pin", "read", "hash_bytes"))


def scan(scanner, streams):
    result = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-public-history-redacted-") as path:
        for label, stream in streams.items():
            report = Path(path) / (label + ".json")
            command = [scanner, "stdin", "--redact=100", "--no-banner", "--no-color",
                       "--report-format=json", "--report-path", report]
            data = stream.getvalue()
            child = subprocess.run(command, input=data, capture_output=True, timeout=90, check=False)
            found = read(report) if report.exists() else []
            result[label] = dict(actualExit=child.returncode, sha256=digest(data), bytes=len(data),
                rules=dict(Counter(item["RuleID"] for item in found)),
                signalLocations=[dict(rule=item["RuleID"], start=item["StartLine"], end=item["EndLine"])
                                 for item in found])
    return result


def add(stream, header, data):
    first = stream.getvalue().count(b"\n") + 1
    stream.write(f"\n{header}\n".encode())
    stream.write(data)
    stream.write(b"\n")
    assert stream.tell() <= H["MAX_BATCH"]
    return (first + 2, first + 2 + data.count(b"\n"))


def main(start_pattern="878_*"):
    start = read(next(PLAN.glob(start_pattern)))
    v = start["values"]
    runner = Path(__file__).relative_to(Path.cwd()).as_posix()
    for ref in v["oracleReferences"]:
        path = ref["path"]
        if path == runner:
            assert digest(git("show", v["source"] + ":" + path)) == ref["sha256"]
        else:
            assert pin(path) == ref
    previous = read(v["oracleReferences"][1]["path"])
    assert previous["actualExit"] == 0
    if "secretFindings" in previous:
        assert previous["secretFindings"] == 0
    else:
        assert set(previous["scans"]) == {"textCommitDiffs", "gzipPublicStreams"}
        assert all(result["actualExit"] == 0 and not result["signalLocations"]
                   for result in previous["scans"].values())
    old, new = previous["newCursor"], v["source"]
    assert git("merge-base", old, new).decode().strip() == old
    commits = git("rev-list", "--reverse", old + ".." + new).decode().splitlines()
    assert 5 <= len(commits) <= 25
    scanner = (Path.cwd().parent / "toolchain/gitleaks-8.30.1-linux-x64/gitleaks").resolve()
    prior_scanner = previous.get("tool")
    if prior_scanner is None:
        first_scan = read(previous["firstResult"]["path"])
        prior_scanner = first_scan["scanner"]
    assert pin(scanner) == prior_scanner
    data = {label: io.BytesIO() for label in ("textCommitDiffs", "gzipPublicStreams")}
    paths, binary, zipped = {}, [], []
    for commit in commits:
        parent = git("rev-parse", commit + "^").decode().strip()
        files = git("diff", "--no-renames", "--numstat", "-z", parent, commit)
        for row in files.split(b"\0"):
            if not row:
                continue
            count_a, count_d, filename = row.decode().split("\t", 2)
            path = Path(filename)
            if (count_a, count_d) != ("-", "-"):
                text = git("diff", "--no-ext-diff", "--no-textconv", "--text", "--no-renames",
                           "--unified=0", parent, commit, "--", filename)
                add(data["textCommitDiffs"], filename + " " + commit, text)
                paths[filename] = paths.get(filename, 0) + 1
                continue
            raw = git("show", commit + ":" + filename)
            if path.suffix == ".gz" and path.is_relative_to(OPS):
                with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                    content = stream.read(H["MAX_LOG"] + 1)
                assert len(content) <= H["MAX_LOG"]
                content.decode("utf-8", "strict")
                first, final = add(data["gzipPublicStreams"], filename + " " + commit, content)
                zipped.append(dict(path=filename, commit=commit, compressedSha256=digest(raw),
                                   decodedSha256=digest(content), scanLines=[first, final]))
            else:
                binary.append(dict(path=filename, commit=commit, bytes=len(raw), sha256=digest(raw),
                                   textualScannerApplies=False))
    results = scan(scanner, data)
    success = all(receipt["actualExit"] == 0 and not receipt["signalLocations"]
                  for receipt in results.values())
    output = OPS / v["run"]
    output.mkdir()
    report = output / "manifest.json"
    record = dict(actualExit=0 if success else 1, source=new, productionCore=v["productionCoreMain"],
                  previousCursor=old, newCursor=new if success else None, commits=commits,
                  textPathVersions=paths, gzipVersions=zipped, binaryMetadataOnly=binary,
                  tool=pin(scanner), runner=pin(runner), scans=results, rawFindingSecretsPersisted=0,
                  excludedPrivateArchivesRead=0, full451Accepted=False, wholeG07Accepted=False,
                  terminalAtUTC=H["datetime"].now(H["timezone"].utc).isoformat())
    with report.open("x") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(pin(report), len(commits), len(paths), len(zipped), len(binary),
          {k: (v["actualExit"], len(v["signalLocations"])) for k, v in results.items()})
    return record["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
