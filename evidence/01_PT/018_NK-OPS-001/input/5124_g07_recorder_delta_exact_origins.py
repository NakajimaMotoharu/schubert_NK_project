"""Resolve only coordinate-bound matches with independently verified public origins."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
OUT = EVIDENCE / "PG39284-g07-published-recorder-delta-v1"
PROJECTION = Path.cwd().parent / "pgpt-runs/PG379" / OUT.name.lower()
ORIGINAL = EVIDENCE / "PG39246-f03-api-jvm-system-independent-v1/manifest.json"
PREPARE = Path.cwd().parent / "pgpt-runs/PG379/pg39234-bug3262-api-jvm-system-prepare-v1"
JAVA_DIR = "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/"
CLASS_DIR = "dev/codex/schubert/nk/api/monitoring/"
GIT_HEX = re.compile(rb"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
HASH_FIELD = re.compile(rb'\s*"([^"]+)"\s*:\s*"([0-9a-f]{64})"\s*,?')


def load(path):
    return json.loads(path.read_bytes())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(path):
    return {"path": str(path), "sha256": digest(path.read_bytes())}


def git(*args):
    return subprocess.check_output(["git", *args], timeout=60)


def save(path, data):
    with path.open("x") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def generic_origin(line, lo, hi, unit, compiled, witness):
    m = HASH_FIELD.fullmatch(line)
    if not m or max(0, min(m.end(2), hi + 1) - max(m.start(2), lo - 1)) < 63:
        return None
    key, sha = (v.decode() for v in m.groups())
    if key in {JAVA_DIR + n + ".java" for n in ("ApiJvmMetrics", "ApiSystemMetrics")}:
        assert compiled["inputHashes"][key] == sha
        assert digest(git("show", f'{unit["productionCoreMain"]}:{key}')) == sha
        return dict(kind="exact API production source at the declared commit",
                    source=unit["productionCoreMain"], path=key, reviewedUnit=ref(ORIGINAL))
    if key in {CLASS_DIR + n + ".class" for n in ("ApiJvmMetrics", "ApiSystemMetrics", "ApiJvmMetricsTest")}:
        test = key.endswith("Test.class")
        path = PREPARE / ("test-classes" if test else "component") / key
        assert path.resolve() == path and path.is_file() and not path.is_symlink()
        assert compiled["testClassHashes" if test else "physicalClassHashes"][key] == sha
        assert digest(path.read_bytes()) == sha
        return dict(kind="exact closed-host compiled class bytes",
                    classPath=key, source=unit["source"], preparedManifest=witness)
    return None


def git_origin(row, line, lo, hi, reachable):
    matches = [m for m in GIT_HEX.finditer(line)
               if max(0, min(m.end(), hi + 1) - max(m.start(), lo - 1)) >= 39]
    if len(matches) != 1 or matches[0][0] not in reachable:
        return None
    obj = matches[0][0].decode()
    kind = git("cat-file", "-t", obj).strip().decode()
    path = Path(row["path"])
    if kind == "blob" and path.name == "classified-findings.json" and re.fullmatch(rb'\s*"blob": "[0-9a-f]{40}",?', line):
        return dict(kind="reachable Git blob identity at raw byte offsets", verifiedObjectType=kind)
    if kind == "commit" and path.name.startswith("460_"):
        return dict(kind="reachable Git commit identity at raw byte offsets", verifiedObjectType=kind)
    return None


def main():
    scan = load(OUT / "scan-terminal.json")
    preliminary = load(OUT / "manifest.json")
    pending = load(OUT / "unclassified-findings.json")
    report = PROJECTION / "scanner-redacted.json"
    projection = PROJECTION / "projection.json"
    assert scan["reportSha256"] == ref(report)["sha256"]
    assert scan["projectionSha256"] == ref(projection)["sha256"]
    raws = load(report)
    files = {(r["path"], r["blobOid"]): r for r in load(projection)}
    assert len(pending) == preliminary["unresolvedCandidates"]
    unit = load(ORIGINAL)
    prepare = unit["proofs"]["prepare"]
    prepare_path = Path(prepare["path"])
    assert ref(prepare_path) == prepare and unit["actualExit"] == 0
    compiled = load(prepare_path)
    assert compiled["actualExit"] == 0
    reachable = set(git("rev-list", "--objects", "--no-object-names", scan["throughCommit"], "origin/main").splitlines())
    resolved = []
    unresolved = []
    for r in pending:
        file = files[r["path"], r["blob"]]
        assert file["treatment"] == "text"
        local = PROJECTION / file["relativeProjection"]
        line = local.read_bytes().splitlines()[r["line"] - 1]
        raw = raws[r["findingIndex"] - 1]
        assert digest(line) == r["lineSha256"]
        assert (raw["StartLine"], raw["RuleID"]) == (r["line"], r["rule"])
        lo, hi = raw["StartColumn"], raw["EndColumn"]
        assert (lo, hi) == (r["startColumn"], r["endColumn"])
        origin = None
        if r["rule"] == "generic-api-key":
            origin = generic_origin(line, lo, hi, unit, compiled, prepare)
        if r["rule"] == "sourcegraph-access-token":
            origin = git_origin(r, line, lo, hi, reachable)
        (resolved if origin else unresolved).append(dict(r, ground=origin))
    categories = Counter(preliminary["categories"])
    categories.update(decision["ground"]["kind"] for decision in resolved)
    assert sum(categories.values()) + len(unresolved) == scan["findingsCount"]
    save(OUT / "exact-origins.json", resolved)
    save(OUT / "outstanding.json", unresolved)
    final = dict(preliminary, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                 confirmedSecrets=0 if not unresolved else None, unresolvedCandidates=len(unresolved),
                 previousUnresolved=len(pending), categories=dict(categories),
                 earlierPartial=ref(OUT / "manifest.json"), exactOrigins=ref(OUT / "exact-origins.json"),
                 outstanding=ref(OUT / "outstanding.json"), productTests=0, wholeG07Accepted=False)
    save(OUT / "final-manifest.json", final)
    print({k: final[k] for k in ("confirmedSecrets", "unresolvedCandidates", "unqualifiedBinary", "categories")})


if __name__ == "__main__":
    main()
