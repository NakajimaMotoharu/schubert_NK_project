"""Scan the post-capacity public range, validating explicitly typed checksum fields first."""

from collections import Counter
import gzip
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
from tempfile import TemporaryDirectory


PREVIOUS = runpy.run_path(str(Path(__file__).with_name("5334_g07_recent_text_and_gzip.py")))
OPS, PLAN, pin, git, digest, read = (PREVIOUS[name] for name in
                                  ("OPS", "PLAN", "pin", "git", "hash_bytes", "read"))
SHA256 = re.compile(r"[0-9a-f]{64}")


def project(value):
    assert isinstance(value, dict) and all(SHA256.fullmatch(item) for item in value.values())
    return dict.fromkeys(value, "VERIFIED_TYPED_SHA256")


def verify_metadata(source, among, pinned_host):
    get = lambda path: git("show", f"{source}:{path}")
    begin = next(OPS.glob("PG40396-*/begin.json"))
    owner = begin.with_name("owner-execution-start.json")
    old_paths = [next(OPS.glob(f"PG404{run}-*/manifest.json")) for run in (14, 16)]
    assert all(str(path) in among for path in [begin, owner, *old_paths])
    prepared = read(begin.with_name("capsule-independent.json"))
    host = read(pinned_host)["pinnedKnownHostsSha256"]
    original, values = {}, {}
    for path in [begin, owner, *old_paths]:
        original[path] = get(path)
        values[path] = json.loads(original[path])
    spec = values[begin]["spec"]
    assert spec["capsuleSha256"] == prepared["preparedBytesSha256"]
    assert len(spec["files"]) == prepared["checkedEntries"] == 326
    assert all(spec["files"]["classes/" + p] == v for p, v in spec["physical"].items())
    assert all(spec["files"]["testclasses/" + p] == v for p, v in spec["tests"].items())
    for field in ("files", "physical", "tests"):
        spec[field] = project(spec[field])
    assert values[owner]["fixedHostKeySha256"] == host and SHA256.fullmatch(host)
    values[owner]["fixedHostKeySha256"] = "VERIFIED_PREVIOUS_HOST_FILE_SHA256"
    physical = [values[path]["inputPhysical"] for path in old_paths]
    assert physical[0] == physical[1] and sum(map(len, physical[0].values())) == 14
    for path in old_paths:
        values[path]["inputPhysical"] = {k: project(v) for k, v in values[path]["inputPhysical"].items()}
    out = {}
    for path, value in values.items():
        projection = json.dumps(value, ensure_ascii=False, indent=2).encode()
        out[str(path)] = dict(original=original[path], projection=projection)
    return out


def main():
    start = read(next(PLAN.glob("851_*")))
    work = start["values"]
    refs = work["oracleReferences"]
    assert all(pin(ref["path"]) == ref for ref in refs)
    previous, first, secret, capsule = map(lambda ref: read(ref["path"]), refs[1:])
    assert previous["actualExit"] == first["actualExit"] == secret["actualExit"] == capsule["actualExit"] == 0
    assert secret["secretFindings"] == first["findings"] == 0
    old, new = previous["endCursor"], work["source"]
    assert git("merge-base", old, new).decode().strip() == old
    counts = {}
    for line in git("diff", "--no-renames", "--numstat", "-z", old, new).split(b"\0"):
        if line:
            added, removed, name = line.decode().split("\t", 2)
            counts[name] = (added, removed)
    projected = verify_metadata(new, counts, next(OPS.glob("PG40160-*/begin.json")))
    assert all(counts[name][1] == "0" for name in projected)
    txt, zipped, binary = [], [], []
    for name, num in sorted(counts.items()):
        if name in projected:
            continue
        if name.startswith(str(OPS) + "/") and name.endswith(".gz") and num == ("-", "-"):
            zipped.append(name)
        elif num == ("-", "-") or name.endswith(".exec"):
            binary.append(name)
        else:
            txt.append(name)
    payloads = {
        "textPatch": git("diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--text", old, new, "--", *txt),
        "projectedMixedMetadata": b"\n".join(row["projection"] for row in projected.values()),
    }
    logs, details = io.BytesIO(), []
    for path in zipped:
        raw = git("show", f"{new}:{path}")
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as body:
            final = body.read(PREVIOUS["MAX_LOG"] + 1)
        assert len(final) <= PREVIOUS["MAX_LOG"] and logs.tell() + len(final) <= PREVIOUS["MAX_BATCH"]
        final.decode("utf-8", "strict")
        logs.write(final + b"\n")
        details.append(dict(path=path, compressedSha256=digest(raw), decodedSha256=digest(final),
                            decodedBytes=len(final)))
    payloads["gzipLogs"] = logs.getvalue()
    verified_binary = []
    for name in binary:
        raw = git("show", f"{new}:{name}")
        verified_binary.append(dict(path=name, sha256=digest(raw), size=len(raw),
                                    textualSecretScannerCoverage=False))
    gitleaks = Path("../toolchain/gitleaks-8.30.1-linux-x64/gitleaks").resolve()
    result = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-published-capacity-bom-") as name:
        temp = Path(name)
        for label, data in payloads.items():
            report = temp / (label + ".json")
            command = [str(gitleaks), "stdin", "--redact=100", "--no-banner", "--no-color",
                       "--report-format=json", f"--report-path={report}"]
            run = subprocess.run(command, input=data, capture_output=True, timeout=80)
            alerts = read(report) if report.is_file() else []
            result[label] = dict(actualExit=run.returncode, count=len(alerts),
                                 rules=dict(Counter(row["RuleID"] for row in alerts)),
                                 bytes=len(data), sha256=digest(data))
    success = all(receipt["actualExit"] == receipt["count"] == 0 for receipt in result.values())
    out = OPS / work["run"]
    out.mkdir()
    output = out / "manifest.json"
    metadata = {name: {which + "Sha256": digest(data) for which, data in entry.items()}
                for name, entry in projected.items()}
    data = dict(actualExit=0 if success else 1, source=new, productionCore=work["productionCoreMain"],
                previousCursor=old, newCursor=new if success else None, verifiedTextPaths=len(txt),
                gzipPaths=details, typedMetadata=metadata, binaryMetadata=verified_binary,
                deltaCommits=int(git("rev-list", "--count", f"{old}..{new}").strip()),
                scanner=pin(gitleaks), scans=result, rawSecretValuesSaved=0, sourceEvidence=refs,
                wholeG07Accepted=False, whole451Accepted=False, actualProductTests=0,
                terminalAtUTC=PREVIOUS["datetime"].now(PREVIOUS["timezone"].utc).isoformat())
    with output.open("x") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(output), success, len(txt), len(details), len(verified_binary), result)
    return data["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
