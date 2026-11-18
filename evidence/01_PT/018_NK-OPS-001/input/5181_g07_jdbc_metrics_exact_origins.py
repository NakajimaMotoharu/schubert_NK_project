"""Independently prove outstanding scanner coordinates from exact source and run artifacts."""
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import subprocess

SPEC = spec_from_file_location("scope_wrapper", Path(__file__).with_name("5180_g07_jdbc_metrics_delta.py"))
WRAPPER = module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)
BASE, OUT, WORK = WRAPPER.BASE / "evidence", WRAPPER.OUT, WRAPPER.TEMP
BIND = WRAPPER.load_stage("bind")
PRIOR = BASE / "PG39430-g07-quality-published-delta-v1"
RUNS = WRAPPER.RETAIN.parent
CLASS_PACKAGES = frozenset(("storage", "api", "protocol", "web"))
PREPARE_RUNS = (
    "PG39332", "PG39350", "PG39368", "PG39387", "PG39423",
    "PG39481", "PG39504", "PG39522", "PG39541", "PG39558",
)
ORDINARY_BUILD_RUNS = ("PG39434", "PG39458", "PG39462")
DIRECT_BUILD_NAMESPACE = "dev/codex/schubert/nk/api/bootstrap/"
DIRECT_BUILD_NAMES = frozenset((
    "ServiceDatabaseAdmission.class", "ServiceDatabaseAdmission$1.class",
    "ServiceDatabaseSource.class", "ServiceDatabaseSource$Connector.class",
    "JdbcFailureGraph.class", "JdbcAdmissionFailures.class",
))
OWNED_BUILD_SUFFIXES = frozenset((
    "PG39438-service-jdbc-ports-unit-v1",
    "PG39464-ssc468-admission-ports-unit-v1",
))
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
    for run in ORDINARY_BUILD_RUNS:
        paths = list(BASE.glob(run+"-*/compile/manifest.json"))
        assert len(paths)==1
        p = paths[0]
        m = BIND.load(p)
        assert m["actualExit"]==0 and m["inputHashesReverified"]
        folder = Path(m["cwd"])
        assert folder.is_relative_to(RUNS) and folder.resolve()==folder
        base = folder / "src/schubert-nk-bootstrap/target/classes"
        known = m["physicalClassHashes"]["bootstrap"]
        for name in DIRECT_BUILD_NAMES:
            rel = DIRECT_BUILD_NAMESPACE+name
            if rel not in known:
                continue
            sha = known[rel]
            file = base / rel
            if file.is_file() and file.resolve()==file and BIND.sha(file.read_bytes())==sha:
                checked[(rel,sha)] = dict(kind="Exact class bytes from fixed four-module normal build",
                    classPath=rel, module="bootstrap", prepare=BIND.ref(p))
    return checked


def prior_index():
    prior_private = RUNS / PRIOR.name.lower() / "projection.json"
    prior_scan = BIND.load(PRIOR / "scan-terminal.json")
    assert BIND.ref(prior_private)["sha256"] == prior_scan["projectionSha256"]
    known = {}
    for p in ("scan-terminal.json", "adjudication-first.json", "classified-findings.json", "independent-additional-origins.json"):
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
    if not re.fullmatch(r"dev/codex/schubert/nk/(api|web|storage)/[A-Za-z0-9_/$]+",key):
        return None
    if Path(key).stem.split("$")[0] in BIND.HELD or len(value)!=16 or location.name!="manifest.json":
        return None
    match = location.parent.name
    if not any(match.startswith(run+"-") for run in ("PG39428","PG39488","PG39514","PG39532","PG39550","PG39568")):
        return None
    manifest = BIND.load(location)
    if value != manifest["classIds"].get(key):
        return None
    measurement = location.with_name("unit-execinfo.stdout")
    if BIND.ref(measurement)["sha256"] != manifest["files"][measurement.name]:
        return None
    exact = [line for line in measurement.read_text().splitlines() if line.split() and line.split()[-1] == key]
    if len(exact)==1 and exact[0].split()[0]==value:
        return dict(kind="Trace class identity in same admitted JaCoCo execinfo",
                    unit=BIND.ref(location), execinfo=BIND.ref(measurement))
    return None


def extra_binary(rows, by_key, scan):
    recognized = []
    for row in rows:
        if row.get("actualExit")==0:
            continue
        path=Path(row["path"])
        if path.name!="jacoco.exec" or path.parent.name not in OWNED_BUILD_SUFFIXES:
            continue
        manifest=path.with_name("manifest.json")
        m=BIND.load(manifest)
        key=(row["path"],row["blob"])
        original=by_key[key]
        target=WORK/original["relativeProjection"]
        sha=BIND.sha(target.read_bytes())
        assert sha==original["blobSha256"]==m["files"]["jacoco.exec"]
        assert m["actualExit"]==0 and m["tests"]==31 and m["stages"]["execinfo"]["actualExit"]==0
        proof=manifest.with_name("execinfo.stdout")
        if not proof.is_file():
            from gzip import decompress
            report=decompress(proof.with_name('execinfo.stdout.gz').read_bytes())
        else:
            report=proof.read_bytes()
        assert BIND.sha(report)==m["stages"]["execinfo"]["stdoutSha256"]
        lines=report.decode().splitlines()
        sessions=[v for v in lines if v.startswith("Session ")]
        probes=[v for v in lines if re.fullmatch(r"[0-9a-f]{16}\s+\d+ of\s+\d+\s+\S+",v)]
        assert len(sessions)==1 and m["run"] in sessions[0] and probes
        recognized.append(dict(row,actualExit=0,owner=BIND.ref(manifest),derivedRows=len(probes),
            scope="Previously recorded single-run JaCoCo class/probe data; no product execution"))
    assert len(recognized)<=len(rows)
    return recognized
