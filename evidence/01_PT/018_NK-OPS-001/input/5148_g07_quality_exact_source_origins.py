"""Independently prove outstanding scanner coordinates from exact source and run artifacts."""
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import subprocess

SPEC = spec_from_file_location("scope_wrapper", Path(__file__).with_name("5147_g07_quality_delta.py"))
WRAPPER = module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)
BASE, OUT, WORK = WRAPPER.EVIDENCE, WRAPPER.OUT, WRAPPER.WORK
BIND = WRAPPER.load_stage("bind")
PRIOR = BASE / "PG39284-g07-published-recorder-delta-v1"
RUNS = WORK.parent
CLASS_PACKAGES = frozenset(("storage", "api", "protocol"))
PREPARE_RUNS = ("PG39332", "PG39350", "PG39368", "PG39387", "PG39423")
FIELD = re.compile(rb'\s*"([^"\\]+)"\s*:\s*"([0-9a-f]{16}|[0-9a-f]{40}|[0-9a-f]{64})"\s*,?')


def tree():
    return BIND.load(WORK / "projection.json")


@lru_cache(maxsize=None)
def stored_blob(oid):
    return BIND.git("cat-file", "blob", oid)


@lru_cache(maxsize=None)
def source_versions(source, path):
    items = BIND.git("log", "--format=%H", source, "origin/main", "--", path).decode().splitlines()
    current = BIND.git("rev-parse", source).decode().strip()
    candidates = list(dict.fromkeys((current, *items)))
    result = {}
    for candidate in candidates:
        proc = subprocess.run(["git", "rev-parse", "--verify", f"{candidate}:{path}"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10)
        if proc.returncode == 0:
            oid = proc.stdout.decode().strip()
            if oid not in result:
                result[oid] = candidate
    return {BIND.sha(stored_blob(oid)): (oid, revision) for oid, revision in result.items()}


def checked_source(path, value, source):
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts or relative.stem in BIND.HELD:
        return None
    if path.startswith("src/") and relative.suffix in (".java", ".template"):
        hit = source_versions(source, path).get(value)
        if hit:
            obj, commit = hit
            return dict(kind="Exact path and content in reachable Git history", path=path, object=obj, commit=commit)
    return None


def prepare_index():
    checked = {}
    for run in PREPARE_RUNS:
        witnesses = list(BASE.glob(run + "-*/manifest.json"))
        assert len(witnesses) == 1
        path = witnesses[0]
        witness = BIND.load(path)
        config = Path(witness["config"]["path"])
        parent = RUNS / path.parent.name.lower()
        assert parent.resolve() == parent and witness["actualExit"] == 0
        if config.is_file():
            assert BIND.ref(config) == witness["config"]
        for key, folder in (("physicalClassHashes", "component"), ("testClassHashes", "test-classes")):
            for p, claimed in witness[key].items():
                relative = Path(p)
                if (relative.is_absolute() or ".." in relative.parts or relative.stem.split("$")[0] in BIND.HELD
                        or relative.parts[:4] != ("dev", "codex", "schubert", "nk")
                        or relative.parts[4] not in CLASS_PACKAGES):
                    continue
                candidate = parent / folder / relative
                assert candidate.resolve() == candidate and not candidate.is_symlink()
                if candidate.is_file() and BIND.sha(candidate.read_bytes()) == claimed:
                    checked[(p, claimed)] = dict(kind="Exact compiled closed-host class bytes",
                        classPath=p, artifactKind=folder, prepare=BIND.ref(path))
    return checked


def prior_index():
    prior_private = RUNS / PRIOR.name.lower() / "projection.json"
    prior_scan = BIND.load(PRIOR / "scan-terminal.json")
    assert BIND.ref(prior_private)["sha256"] == prior_scan["projectionSha256"]
    known = {}
    for p in ("scan-terminal.json", "adjudication-first.json", "classified-findings.json"):
        file = PRIOR / p
        m = BIND.load(file)
        known[p] = (BIND.ref(file), m["findings"] if isinstance(m, dict) else m)
    rows = BIND.load(prior_private)
    assert len(rows) == prior_scan["trackedBlobVersions"]
    return known, {(r["path"], r["blobOid"]): r for r in rows}


def checked_prior(location, field, value, prior, index):
    if location.parent != PRIOR or field not in ("lineSha256","blob"):
        return None
    witness, old = prior[location.name]
    for item in old:
        if item.get(field) != value:
            continue
        meta = index.get((item["path"],item["blob"]))
        if meta is None or meta["treatment"] != "text" or meta.get("gzipExpanded"):
            continue
        raw = stored_blob(item["blob"])
        if BIND.sha(raw) != meta["blobSha256"]:
            continue
        if BIND.sha(raw.splitlines()[item["line"] - 1]) == item["lineSha256"]:
            return dict(kind="Prior scanner finding fields match original Git blob and line bytes",
                        priorReport=witness, provedField=field, originalObject=item["blob"])
    return None


def checked_run_id(location, key, value):
    if (location.parent.name != "PG39378-bug3272-api-context-post-v1"
            or key != "dev/codex/schubert/nk/api/monitoring/ApiMetricContext"):
        return None
    manifest = BIND.load(location)
    if value != manifest["classIds"][key]:
        return None
    measurement = location.with_name("unit-execinfo.stdout")
    if BIND.ref(measurement)["sha256"] != manifest["files"][measurement.name]:
        return None
    exact = [line for line in measurement.read_text().splitlines() if line.split() and line.split()[-1] == key]
    if len(exact) == 1 and exact[0].split()[0] == value:
        return dict(kind="Tracer class identity in exact JaCoCo execinfo of admitted run",
                    preexistingUnit=BIND.ref(location), execinfo=BIND.ref(measurement))
    return None


def main():
    scan = BIND.load(OUT / "scan-terminal.json")
    run = BIND.load(OUT / "manifest.json")
    indexed = {(r["path"], r["blobOid"]): r for r in tree()}
    assert BIND.ref(WORK / "projection.json")["sha256"] == scan["projectionSha256"]
    assert BIND.ref(WORK / "scanner-redacted.json")["sha256"] == scan["reportSha256"]
    rows = BIND.load(OUT / "unclassified-findings.json")
    assert len(rows) == run["unresolvedCandidates"]
    classes = prepare_index()
    prior, prior_blobs = prior_index()
    resolutions, remaining = [], []
    for r in rows:
        version = indexed[r["path"], r["blob"]]
        p = WORK / version["relativeProjection"]
        decoded = p.read_bytes()
        assert BIND.sha(decoded) == version["decodedSha256"]
        line = decoded.splitlines()[r["line"] - 1]
        assert BIND.sha(line) == r["lineSha256"]
        field = FIELD.fullmatch(line)
        decision = None
        if field and max(field.start(2), r["startColumn"] - 1) < min(field.end(2), r["endColumn"]):
            key, value = (g.decode() for g in field.groups())
            location = Path(r["path"])
            if r["rule"] == "generic-api-key":
                decision = checked_source(key, value, scan["throughCommit"]) or classes.get((key, value))
                if decision is None:
                    decision = checked_run_id(location, key, value)
            if r["rule"] == "sourcegraph-access-token":
                decision = checked_prior(location, key, value, prior, prior_blobs)
        if decision is None:
            remaining.append(r)
        else:
            resolutions.append(dict(r, ground=decision))
    assert len(resolutions) + len(remaining) == len(rows)
    counts = Counter(run["categories"])
    counts.update(r["ground"]["kind"] for r in resolutions)
    assert sum(counts.values()) + len(remaining) == scan["findingsCount"]
    a = OUT / "independent-additional-origins.json"
    r = OUT / "remaining-origins.json"
    BIND.write(a, resolutions)
    BIND.write(r, remaining)
    result = dict(run, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        originalClassification=BIND.ref(OUT / "manifest.json"), additionalOrigins=BIND.ref(a),
        remaining=BIND.ref(r), categories=dict(counts), unresolvedCandidates=len(remaining),
        confirmedSecrets=0 if not remaining else None, resultQualifiedForRange=not remaining and not run["unqualifiedBinary"])
    BIND.write(OUT / "origins-pass2.json", result)
    print(dict(categories=dict(counts), unresolved=len(remaining),
               remainingFiles=Counter(Path(row["path"]).name for row in remaining)))


if __name__ == "__main__":
    main()
