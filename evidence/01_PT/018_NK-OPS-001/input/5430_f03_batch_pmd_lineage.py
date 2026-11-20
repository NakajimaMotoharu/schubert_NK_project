"""Review which previously admitted Batch PMD receipts survive the current binary changes."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[4]
PLAN = next((ROOT / "documents/400_PGPT/470_PMO").glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
BATCH = "src/schubert-nk-batch/src/main/java/"
HELD = {"TemporaryInfrastructureException", "FingerprintKeyRing",
        "ResponseSnapshotCodec", "WebStartupException"}


def pin(path):
    return {"path": str(path), "sha256": sha256(Path(path).read_bytes()).hexdigest()}


def verified(ref):
    assert pin(ref["path"]) == ref
    return Path(ref["path"])


def read(p):
    return json.loads(Path(p).read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=15)


def source(binary):
    return BATCH + binary.split("$", 1)[0].replace(".", "/") + ".java"


def main():
    start = read(next(PLAN.glob("1114_F03Batch*")))
    v = start["values"]
    refs = v["oracleReferences"]
    for ref in refs:
        verified(ref)
    original, decisions, expiry, cleanup, graph, package = [read(r["path"]) for r in refs[1:]]
    core = v["productionCoreMain"]
    old = original["productionCore"]
    assert decisions["productionCore"] == old
    assert cleanup["core"] == graph["productionCore"] == package["candidateProductionSource"] == core
    assert git("rev-parse", "HEAD").decode().strip() == v["source"]
    assert not git("diff", "--name-only", core, "--", "src", "pom.xml")
    expiry_source = next(r for r in expiry["sourceEvidence"]
                         if r["path"].endswith("/ExpiryAuditRepository.java"))
    verified(expiry_source)
    verified(cleanup["target"])
    target_sources = {expiry_source["path"], cleanup["target"]["path"]}
    changed_source = set(git("diff", "--name-only", old, core, "--", "src", "pom.xml",
                             ":(exclude)src/**/src/test/**").decode().splitlines())
    assert changed_source == target_sources
    assert original["rules"]["sha256"] == cleanup["fixedRules"]["sha256"]
    admitted = read(verified(original["inputs"]))
    source_pins = admitted["sources"]
    assert len(source_pins) == original["sourceCount"] == 128
    differing_sources = {name for name, digest in source_pins.items()
                         if pin(ROOT / name)["sha256"] != digest}
    assert differing_sources == changed_source
    values = admitted["selectedBatchTypes"]
    actual = verified(package["privateJars"]["batch"]["artifact"])
    with ZipFile(actual) as archive:
        assert not any(Path(n).stem.split("$")[0] in HELD for n in values)
        current_types = {n: sha256(archive.read(n)).hexdigest() for n in values}
    differing_types = {n for n in values if current_types[n] != values[n]}
    assert {source(n[:-6].replace("/", ".")) for n in differing_types} == changed_source
    for row, collected in [(cleanup, cleanup["physical"]), (expiry, None)]:
        if collected is not None:
            assert all(current_types[name] == digest for name, digest in collected.items())
        else:
            p = next(x for x in row["sourceEvidence"] if "PG40736-" in x["path"])
            current = read(verified(p))
            assert all(current_types[name] == digest
                       for name, digest in current["physicalHashes"].items())
    inbound = defaultdict(set)
    data = gzip.decompress(verified(graph["raw"][0]).read_bytes()).decode()
    for line in data.splitlines():
        if line.startswith(" ") and " -> " in line:
            a, _, b, _ = line.split(None, 3)
            inbound[source(b)].add(source(a))
    affected = set(changed_source)
    frontier = set(changed_source)
    while frontier:
        more = set().union(*(inbound[target] for target in frontier)) - affected
        affected.update(more)
        frontier = more
    affected_admitted = (affected & set(source_pins)) - changed_source
    stable = set(source_pins) - affected
    raw = ET.parse(verified(original["raw"]))
    counts = Counter()
    for node in raw.getroot():
        name = node.get("name", "")
        if f"/{BATCH}" in name:
            path = BATCH + name.split(f"/{BATCH}", 1)[1]
            assert path in source_pins
            counts[path] += len([item for item in node if item.tag.endswith("}violation")])
    assert sum(counts.values()) == original["rawFindings"] == 397
    pending = Counter(row["path"] for row in read(verified(decisions["pending"])))
    assert sum(pending.values()) == decisions["unclassified"] == 12
    assert all(pending[path] <= counts[path] for path in pending)
    previous_stable_raw = sum(counts[path] for path in stable)
    old_pending_stable = sum(pending[path] for path in stable)
    known = previous_stable_raw - old_pending_stable
    broadened = sum(counts[p] for p in affected_admitted)
    terminal = datetime.now(timezone.utc).isoformat()
    result = dict(
        actualExit=0, source=v["source"], productionCore=core, previousCore=old,
        startEvent=start["eventId"], terminalAtUTC=terminal, inputs=refs, runner=pin(Path(__file__)),
        admittedMain=len(source_pins), omittedOriginalMain=original["sourceExcluded"],
        previouslyAdmittedPhysical=len(values), identicalPriorPhysical=len(values)-len(differing_types),
        changedPhysical=sorted(differing_types), changedMain=sorted(changed_source),
        stableSourceCount=len(stable), stableSourceHashes={p: source_pins[p] for p in sorted(stable)},
        dependencyRefreshNeeded={p: counts[p] for p in sorted(affected_admitted)},
        dependencyRefreshNeededOldRaw=broadened, oldRawStableScope=previous_stable_raw,
        oldDispositionsEligibleForLineageReview=known,
        priorUnclassifiedStillOpen={p: pending[p] for p in sorted(pending)},
        actualCurrentChangedRaw={expiry_source["path"]: expiry["pmdRaw"],
                                 cleanup["target"]["path"]: cleanup["pmdRaw"]},
        cleanupCurrentReviewed=24, cleanupCurrentUnclassified=24,
        expiryCurrentReviewed=expiry["classifiedNonApplicable"], expiryCurrentUnclassified=expiry["unclassified"],
        fullScopePmDReplayed=False, dynamicCases=0, newFormalAcceptance=0, wholeF03=False, whole451=False,
    )
    out = OPS / v["run"]
    out.mkdir()
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print({k: result[k] for k in ("admittedMain", "stableSourceCount", "identicalPriorPhysical",
                                  "dependencyRefreshNeeded", "oldRawStableScope",
                                  "oldDispositionsEligibleForLineageReview", "actualCurrentChangedRaw")})


if __name__ == "__main__":
    main()
