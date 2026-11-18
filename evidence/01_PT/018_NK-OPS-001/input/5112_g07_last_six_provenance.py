"""Close the six remaining candidates from their fixed compiled and Git identities."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path("evidence/01_PT/018_NK-OPS-001")
OUT = BASE / "evidence/PG39196-g07-current-published-delta-v1"
RUNS = Path.cwd().parent / "pgpt-runs/PG379"
WORK = RUNS / "pg39196-g07-current-published-delta-v1"
TEST = "dev/codex/schubert/nk/api/idempotency/SecretBufferTest.class"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def write(path, data):
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def git(*args):
    return subprocess.check_output(["git", *args], timeout=30)


def main():
    preliminary = load(OUT / "manifest.json")
    scan = load(OUT / "scan-terminal.json")
    head = scan["throughCommit"]
    rows = load(WORK / "projection.json")
    assert ref(WORK / "projection.json")["sha256"] == scan["projectionSha256"]
    by_blob = {(r["path"], r["blobOid"]): r for r in rows}
    candidates = load(OUT / "unclassified-findings.json")
    assert len(candidates) == preliminary["unresolvedCandidates"] == 6

    profile_file = BASE / "input/5103_ssc466_buffer_diagnostic_profile.json"
    profile = load(profile_file)
    prep_path = Path(profile["slots"]["prepare"]) / "manifest.json"
    prep = load(prep_path)
    assert prep["config"] == ref(profile_file) and prep["actualExit"] == 0
    directory = RUNS / profile["privateDirs"]["prepare"] / "test-classes"
    exact_class = directory / TEST
    assert directory.name == "test-classes" and directory.parent.name == "pg39132-ssc466-buffer-diagnostic-prepare-v1"
    assert exact_class.is_file() and exact_class.resolve() == exact_class
    class_digest = sha(exact_class.read_bytes())
    assert prep["testClassHashes"][TEST] == class_digest

    origins = []
    for x in candidates:
        meta = by_blob[x["path"], x["blob"]]
        line = (WORK / meta["relativeProjection"]).read_bytes().splitlines()[x["line"] - 1]
        assert sha(line) == x["lineSha256"]
        lo, hi = x["startColumn"] - 1, x["endColumn"]
        if x["rule"] == "generic-api-key":
            m = re.fullmatch(rb'\s*"([^"]+)"\s*:\s*"([0-9a-f]{64})"\s*,?', line)
            assert m is not None and m[1].decode() == TEST and m[2].decode() == class_digest
            assert max(0, min(m.end(2), hi + 1) - max(m.start(2), lo - 1)) >= 63
            origin = dict(kind="exact same compiled test fixture bytes", classPath=TEST, prepare=ref(prep_path))
        else:
            assert x["rule"] == "sourcegraph-access-token" and "460_" in Path(x["path"]).name
            positioned = [m for m in re.finditer(rb"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", line)
                          if max(0, min(m.end(), hi + 1) - max(m.start(), lo - 1)) >= 39]
            assert len(positioned) == 1
            candidate = positioned[0][0].decode()
            assert git("cat-file", "-t", candidate) == b"commit\n"
            subprocess.run(["git", "merge-base", "--is-ancestor", candidate, head],
                           check=True, capture_output=True, timeout=15)
            origin = dict(kind="reachable Git commit bound using scanner byte columns", verifiedObjectType="commit")
        origins.append(dict(x, ground=origin))
    categories = Counter(preliminary["categories"])
    categories.update(x["ground"]["kind"] for x in origins)
    assert sum(categories.values()) == scan["findingsCount"]
    write(OUT / "late-provenance.json", origins)
    final = dict(preliminary, confirmedSecrets=0, unresolvedCandidates=0, categories=dict(categories),
                 independentStageBefore=ref(OUT / "manifest.json"), supplement=ref(OUT / "late-provenance.json"),
                 supersededUnresolvedCount=6, finalReadUntracked=0, newPrivateRuntimeReads=0,
                 terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(OUT / "final-manifest.json", final)
    print(dict(finalCategories=dict(categories), unresolved=0, binary=preliminary["binary"]))


if __name__ == "__main__":
    main()
