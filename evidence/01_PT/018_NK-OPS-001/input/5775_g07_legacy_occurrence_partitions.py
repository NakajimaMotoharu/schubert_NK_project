"""Reconstruct legacy WBS finding partitions from the published redacted metadata only."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile


EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
ORIGIN_FIELDS = ("path", "ruleId", "startLine", "endLine", "inputSha256")
READABLE_CONFIG_CLASSES = {
    "dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfig.class",
    "dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfig.class",
}
HEX64 = re.compile(r"[0-9a-f]{64}")
JSON_PAIR = re.compile(rb'\s*("(?:[^"\\]|\\.)+")\s*:\s*"([a-f0-9]{64})"\s*,?')


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def data(path):
    return json.loads(path.read_bytes())


def matching_refs(tag):
    path, = EVIDENCE.glob(tag + "*/manifest.json")
    return path


def content(reference):
    path = Path(reference["path"])
    assert path.is_file() and path.is_relative_to("evidence/01_PT") and path.resolve() == path.absolute()
    assert pin(path) == reference
    return data(path)


def key(row):
    path, rule, first, last, digest = (row[name] for name in ORIGIN_FIELDS)
    assert isinstance(path, str) and isinstance(rule, str) and HEX64.fullmatch(digest)
    assert type(first) is type(last) is int and 0 < first <= last
    return path, rule, first, last, digest


def frozen_partition():
    manifest_path = matching_refs("PG24612")
    manifest = data(manifest_path)
    metadata = manifest["originalMetadata"]
    original = content(metadata)
    assert len(original) == 4493
    updates = [*manifest["priorUpdateRefs"],
               dict(path=str(manifest_path.with_name("updates.json")), sha256=manifest["updatesSha256"])]
    closed = set()
    for source in updates:
        individual = list(map(key, content(source)))
        assert len(individual) == len(set(individual)) and closed.isdisjoint(individual)
        closed.update(individual)
    residual = [(ordinal, row) for ordinal, row in enumerate(original, 1) if key(row) not in closed]
    assert len(closed) == 1213 and len(residual) == 3280
    assert len(original) - len(residual) == len(closed)
    bins = [residual[index:index+410] for index in range(0, len(residual), 410)]
    assert len(bins) == 8 and all(len(group) == 410 for group in bins)
    return manifest_path, metadata, bins


def compare_public_config_only(first):
    public_metadata = EVIDENCE / "provisional/PG313-regression-2201/manifest.json"
    approved_lines = {1013, 1381}
    candidates = [(ordinal, row) for ordinal, row in first
                  if row["path"] == str(public_metadata) and row["startLine"] in approved_lines]
    assert len(candidates) == 2
    assert all(pin(public_metadata)["sha256"] == row["inputSha256"] for _, row in candidates)
    raw = public_metadata.read_bytes().splitlines()
    prior = data(matching_refs("PG43066"))["normalArtifacts"]["bootstrap"]["jar"]
    jar_path = Path(prior["path"])
    assert pin(jar_path) == prior
    result = []
    with ZipFile(jar_path) as archive:
        for ordinal, row in candidates:
            assert row["startLine"] == row["endLine"] and row["shape"] == "ALL_HEX64"
            assert row["uniqueExactCaptureCount"] == 1 and row["captureLengths"] == [64]
            token = JSON_PAIR.fullmatch(raw[row["startLine"]-1])
            assert token
            name = json.loads(token[1])
            assert name in READABLE_CONFIG_CLASSES
            current = hashlib.sha256(archive.read(name)).hexdigest()
            same = token[2].decode() == current
            result.append(dict(sourceOrdinal=ordinal, qualifiedType=name, currentArchiveMatch=same))
    return dict(reportedInput=pin(public_metadata),approvedCurrentArchive=prior,comparisons=result)


def id_digest(ordinals):
    return hashlib.sha256("\n".join(map(str, ordinals)).encode()).hexdigest()


def main():
    origin, shape, partitions = frozen_partition()
    first = partitions[0]
    comparison = compare_public_config_only(first)
    classified = {r["sourceOrdinal"] for r in comparison["comparisons"] if r["currentArchiveMatch"]}
    assert classified <= {ordinal for ordinal, _ in first}
    record = {
        "run": "PG43116-g07-archived-first410-public-provenance-v1",
        "actualExit": 0,
        "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
        "source": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "productCore": "87927ea17c1c8dbef528bc0c6882c24b1fe7c871",
        "wbs": "WBS-G07/01",
        "shapeMetadata": shape,
        "archiveAccounting": pin(origin),
        "identifierDefinition": "One-based original metadata row ordinal, scoped to the exact shapeMetadata SHA. Distinct occurrences are retained when the old metadata key repeats.",
        "originalOccurrences": 4493,
        "previousClassified": 1213,
        "currentAuthenticatedResidual": 3280,
        "partitionPins": [
            dict(partition=f"{index:02d}", count=410, ordinalsSha256=id_digest([n for n, _ in bucket]))
            for index, bucket in enumerate(partitions, 1)
        ],
        "sectionOneRows": [dict(id=ordinal, shape=row["shape"],
                                disposition="PUBLIC_CLASS_SHA_MATCH" if ordinal in classified else "PENDING_PROVENANCE")
                           for ordinal, row in first],
        "sectionOneShapes": dict(Counter(row["shape"] for _, row in first)),
        "sectionOneDistinctKeys": len({key(row) for _, row in first}),
        "approvedPublicComparison": comparison,
        "newlyClassifiedSectionOne": len(classified),
        "sectionOneRemaining": 410-len(classified),
        "archivedActualSecretCount": None,
        "privateRawOpenCount": 0,
        "oldHeldClassFileOpenCount": 0,
        "sourceOrBuildInputsMutated": 0,
        "externalOperations": 0,
        "actualNewScanInvoked": False,
        "wholeG07": False,
        "whole451": False,
        "formalAcceptanceId": None,
    }
    out = EVIDENCE / record["run"] / "manifest.json"
    out.parent.mkdir()
    with out.open("x") as f:
        f.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(pin(out), record["sectionOneRemaining"])


if __name__ == "__main__":
    main()
