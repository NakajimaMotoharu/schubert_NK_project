"""Reconcile the second frozen finding group against scoped public reports."""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from runpy import run_path
import subprocess


BASE = Path(__file__).with_name("5775_g07_legacy_occurrence_partitions.py")
ORIGIN = run_path(str(BASE))
EVIDENCE = ORIGIN["EVIDENCE"]
pin = ORIGIN["pin"]
data = ORIGIN["data"]
key = ORIGIN["key"]

REPORT_NAMES = {
    "TEST-dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest.xml",
    "TEST-dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest.xml",
}
REFERENCE = EVIDENCE / "provisional/PG3974-literal-invariant-whole-signed-v1/all-six-results.json"
ORIGINAL_REPORTS = REFERENCE.parent
COMPARISON_REPORTS = EVIDENCE / "provisional/PG15224-nonsecret-config-fourteen-post-v1"


def tracked_reports(source):
    roots = [str(ORIGINAL_REPORTS), str(COMPARISON_REPORTS)]
    entries = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "-z", source, "--", *roots])
    for name in entries.decode().split("\0"):
        if name and Path(name).name in REPORT_NAMES:
            yield Path(name)


def compare_config_report_refs(second, source):
    rows = [(ordinal, row) for ordinal, row in second
            if row["path"] == str(REFERENCE) and ordinal in {474, 485}]
    assert len(rows) == len(REPORT_NAMES)
    reference = pin(REFERENCE)
    assert all(reference["sha256"] == row["inputSha256"] for _, row in rows)
    text_lines = REFERENCE.read_bytes().splitlines()
    public_xml_hashes = data(REFERENCE)["bootstrap"]["xmlHashes"]
    comparison_reports = dict()
    for path in tracked_reports(source):
        comparison_reports.setdefault(path.name, []).append(pin(path))
    result = []
    for ordinal, row in rows:
        assert row["startLine"] == row["endLine"]
        assert row["shape"] == "ALL_HEX64" and row["uniqueExactCaptureCount"] == 1
        assert row["captureLengths"] == [64]
        entry = ORIGIN["JSON_PAIR"].fullmatch(text_lines[row["startLine"] - 1])
        assert entry
        name, capture = json.loads(entry[1]), entry[2].decode()
        assert name in REPORT_NAMES and public_xml_hashes[name] == capture
        available = comparison_reports.get(name, [])
        matches = [report for report in available if report["sha256"] == capture]
        result.append(dict(sourceOrdinal=ordinal, reportName=name, comparisonFiles=len(available),
                           exactPublicMatch=matches))
    return dict(reportedInput=reference, qualifiedComparisons=result)


def main():
    origin, shape, partitions = ORIGIN["frozen_partition"]()
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    previous = ORIGIN["matching_refs"]("PG43116")
    previous_record = data(previous)
    second = partitions[1]
    ordinals = [ordinal for ordinal, _ in second]
    assert previous_record["shapeMetadata"] == shape
    assert previous_record["partitionPins"][1]["ordinalsSha256"] == ORIGIN["id_digest"](ordinals)
    comparison = compare_config_report_refs(second, source)
    classified = {row["sourceOrdinal"] for row in comparison["qualifiedComparisons"]
                  if row["exactPublicMatch"]}
    assert classified <= set(ordinals)
    record = {
        "run": "PG43166-g07-archived-second410-public-provenance-v1",
        "actualExit": 0,
        "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "productCore": "87927ea17c1c8dbef528bc0c6882c24b1fe7c871",
        "wbs": "WBS-G07/02",
        "shapeMetadata": shape,
        "archiveAccounting": pin(origin),
        "previousPartitionProof": pin(previous),
        "verifier": [pin(BASE), pin(Path(__file__).relative_to(Path.cwd()))],
        "sectionTwoOrdinalSha256": ORIGIN["id_digest"](ordinals),
        "sectionTwoRows": [dict(id=ordinal, shape=row["shape"],
                               disposition="PUBLIC_JUNIT_SHA_MATCH" if ordinal in classified else "PENDING_PROVENANCE")
                           for ordinal, row in second],
        "sectionTwoShapes": dict(Counter(row["shape"] for _, row in second)),
        "sectionTwoDistinctKeys": len({key(row) for _, row in second}),
        "approvedPublicComparison": comparison,
        "newlyClassifiedSectionTwo": len(classified),
        "sectionTwoRemaining": 410 - len(classified),
        "remainingArchiveOccurrences": 3280 - len(classified),
        "archivedActualSecretCount": None,
        "privateRawOpenCount": 0,
        "heldArchiveOpenCount": 0,
        "externalOperations": 0,
        "actualNewScanInvoked": False,
        "wholeG07": False,
        "whole451": False,
        "formalAcceptanceId": None,
    }
    out = EVIDENCE / record["run"] / "manifest.json"
    out.parent.mkdir()
    with out.open("x", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(pin(out), record["sectionTwoRemaining"])


if __name__ == "__main__":
    main()
