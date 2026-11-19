"""Check the continued presence of the tested scalar guard without executing fingerprints."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


PLAN = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117")
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
BOUNDARIES = {
    "CanonicalField.java": (b"  public static CanonicalField text(", b"  @Override\n  public String toString"),
    "CanonicalRequest.java": (b"  public CanonicalRequest {", b"  @Override\n  public void close"),
    "OperationFingerprint.java": None,
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def blob(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], timeout=30)


def slice_source(raw, anchors):
    if anchors is None:
        return raw
    start, end = anchors
    assert raw.count(start) == raw.count(end) == 1
    return raw[raw.index(start):raw.index(end)]


def main():
    plan = read(next(PLAN.glob("761_*")))
    v = plan["values"]
    for item in v["oracleReferences"]:
        assert sha(Path(item["path"]).read_bytes()) == item["sha256"]
    universe, unit, independent, diagnostics = (read(ref["path"]) for ref in v["oracleReferences"][1:])
    assert unit["actualExit"] == unit["stages"]["unit"]["actualExit"] == independent["actualExit"] == 0
    assert unit["tests"] == independent["tests"] == 10
    assert unit["failures"] == unit["errors"] == unit["skipped"] == 0
    assert independent["scalarInvalidBoundaryInputs"] == 24 and independent["independentValidGoldenVectors"] == 2
    assert diagnostics["actualExit"] == 0
    numbered = {Path(row["path"]).name: row["index"] for row in universe}
    assert [numbered[name] for name in ("CanonicalField.java", "OperationFingerprint.java")] == [4, 5]
    old = independent["productionCoreMain"]
    core = v["productionCoreMain"]
    exact = []
    for name, anchors in BOUNDARIES.items():
        path = next(path for path in unit["begin"]["inputHashes"] if path.endswith("/" + name))
        before = blob(old, path)
        after = blob(core, path)
        assert sha(before) == unit["begin"]["inputHashes"][path]
        base_contract, current_contract = slice_source(before, anchors), slice_source(after, anchors)
        assert base_contract == current_contract
        exact.append(dict(path=path, methodSourceSha256=sha(current_contract), currentFileSha256=sha(after),
                          originalFileSha256=sha(before), fullSourceEqual=before == after,
                          inventorySite=numbered.get(name)))
    result = dict(actualExit=0, source=v["source"], productionCoreMain=core, historicalTestCore=old,
                  guardScope=exact, historicalCases=10, historicalMalformedInputs=24, historicalGolden=2,
                  originalFailureKept=True, diagnosticChangesOutsideScope=True,
                  conclusion="The tested scalar guards and caller boundary are present in current source. "
                             "The original test is historical scoped guard evidence only.",
                  sourceReferences=v["oracleReferences"], firstValidationSuccessful=True,
                  newProductTests=0, currentCoverageMeasured=False, noFingerprintActions=0,
                  newFormalAcceptance=0, wholeYkt2328Accepted=False, whole451Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = OPS / v["run"]
    out.mkdir()
    manifest = out / "manifest.json"
    with manifest.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(manifest, sha(manifest.read_bytes()))


if __name__ == "__main__":
    main()
