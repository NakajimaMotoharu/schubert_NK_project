"""Confirm remaining scanner positions are fields of the earlier public proof itself."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location

location = Path(__file__).with_name("5124_g07_recorder_delta_exact_origins.py")
spec = spec_from_file_location("blob_origin", location)
verify = module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    out = verify.OUT
    pending = verify.load(out / "outstanding.json")
    partial = verify.load(out / "final-manifest.json")
    scan = verify.load(out / "scan-terminal.json")
    assert len(pending) == partial["unresolvedCandidates"] == 2
    projection = verify.PROJECTION / "projection.json"
    assert verify.ref(projection)["sha256"] == scan["projectionSha256"]
    by_file = {(p["path"], p["blobOid"]): p for p in verify.load(projection)}
    previous = verify.EVIDENCE / "PG39196-g07-current-published-delta-v1"
    previous_scan = verify.load(previous / "scan-terminal.json")
    previous_proof = verify.load(previous / "final-manifest.json")
    classified = previous / "classified-findings.json"
    previous_index = verify.PROJECTION.parent / previous.name.lower() / "projection.json"
    assert verify.ref(previous_index)["sha256"] == previous_scan["projectionSha256"]
    assert verify.ref(classified) == previous_proof["findings"]
    lookup = {p["blobOid"]: p for p in verify.load(previous_index)}
    terminal = []
    for row in pending:
        assert row["path"] == str(classified) and row["rule"] == "sourcegraph-access-token"
        current = by_file[row["path"], row["blob"]]
        assert current["blobSha256"] == previous_proof["findings"]["sha256"]
        decoded = (verify.PROJECTION / current["relativeProjection"]).read_bytes()
        assert verify.digest(decoded) == current["blobSha256"]
        line = decoded.splitlines()[row["line"] - 1]
        m = re.fullmatch(rb'\s*"blob": "([0-9a-f]{40})",?', line)
        assert m and verify.digest(line) == row["lineSha256"]
        assert 1 <= row["startColumn"] < row["endColumn"] <= len(line)
        obj = m[1].decode()
        assert obj in lookup and lookup[obj]["treatment"] == "text"
        assert verify.git("cat-file", "-t", obj) == b"blob\n"
        assert verify.digest(verify.git("cat-file", "blob", obj)) == lookup[obj]["blobSha256"]
        assert any(x["blob"] == obj for x in json.loads(decoded))
        terminal.append(dict(row, ground=dict(kind="prior scanner finding Git blob field by schema and bytes",
            ruleOverlappingOnlyFixedFieldAndObjectId=True, exactPriorScan=verify.ref(previous / "scan-terminal.json"))))
    counts = Counter(partial["categories"])
    counts.update(x["ground"]["kind"] for x in terminal)
    assert sum(counts.values()) == scan["findingsCount"]
    verify.save(out / "prior-blob-field-origins.json", terminal)
    final = dict(partial, confirmedSecrets=0, unresolvedCandidates=0, categories=dict(counts),
        terminalBeforeBlobFieldCheck=verify.ref(out / "final-manifest.json"),
        blobFieldOrigins=verify.ref(out / "prior-blob-field-origins.json"),
        terminalAtUTC=datetime.now(timezone.utc).isoformat())
    verify.save(out / "terminal-manifest.json", final)
    print({k: final[k] for k in ("confirmedSecrets", "unresolvedCandidates", "unqualifiedBinary", "commits", "binary")})


if __name__ == "__main__":
    main()
