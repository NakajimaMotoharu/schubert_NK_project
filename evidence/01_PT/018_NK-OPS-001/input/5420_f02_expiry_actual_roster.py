"""Reconcile the current SSC-461 caller roster and the short-term handoff."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess


E = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PLAN = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
LEGACY = "StorageIoException.preserveFatal("
OWNED = "JdbcFailureGraph.preserveFatal("
MAIN = "src/**/src/main/**"


def read(path):
    return json.loads(Path(path).read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=30)


def rows(rev, path):
    data = git("show", f"{rev}:{path}").decode()
    assert "::preserveFatal" not in data
    return {tag: [line for line, row in enumerate(data.splitlines(), start=1)
                  for _ in range(row.count(tag))] for tag in (LEGACY, OWNED)}


def main():
    start = read(next(PLAN.glob("1061_F02*")))
    v = start["values"]
    assert all(sha256(Path(row["path"]).read_bytes()).hexdigest() == row["sha256"]
               for row in v["oracleReferences"])
    old, expiry, outbox, handoff = [Path(row["path"]) for row in v["oracleReferences"][1:]]
    old_roster, new_expiry, new_outbox = map(read, (old, expiry, outbox))
    assert new_expiry["actualExit"] == new_outbox["actualExit"] == 0
    qualified = v["productionCoreMain"]
    current = v["source"]
    candidate = read(next(PLAN.glob("1057_F02*")))["candidateProductionSource"]
    main_change = new_expiry["candidateSource"]
    target = main_change["path"]
    assert sha256(git("show", f"{candidate}:{target}")).hexdigest() == main_change["sha256"]
    assert not git("diff", "--name-only", candidate, current, "--", MAIN)
    assert git("diff", "--name-only", qualified, current, "--", MAIN).decode().splitlines() == [target]
    changes = git("diff", "--name-only", old_roster["productionCore"], current, "--", MAIN).decode().splitlines()
    by_path = {item["path"]: item.copy() for item in old_roster["exactAnchors"]}
    assert len(by_path) == old_roster["originalNamedMainSources"]
    for path in changes:
        previous = rows(old_roster["productionCore"], path)
        latest = rows(current, path)
        if path not in by_path:
            assert previous == latest == {LEGACY: [], OWNED: []}
            continue
        record = by_path[path]
        assert previous[LEGACY] == record["legacyCurrentLines"]
        assert previous[OWNED] == record["migratedCurrentLines"]
        if path == target:
            assert len(previous[LEGACY]) == 4 and not previous[OWNED] and not latest[LEGACY]
            assert latest[OWNED] == previous[LEGACY] and len(latest[OWNED]) == new_expiry["movedCallEdges"]
        else:
            assert {key: len(value) for key, value in previous.items()} == {
                key: len(value) for key, value in latest.items()
            }
        record["legacyCurrentLines"] = latest[LEGACY]
        record["migratedCurrentLines"] = latest[OWNED]
    counters = {}
    for row in by_path.values():
        subtotal = counters.setdefault(row["module"], Counter())
        subtotal.update(originalSites=row["originalCount"], legacySites=len(row["legacyCurrentLines"]),
                        adapterSites=len(row["migratedCurrentLines"]))
    storage = counters["schubert-nk-storage"]
    assert storage == {"originalSites": 3, "legacySites": 3, "adapterSites": 0}
    upper = [total for module, total in counters.items() if module != "schubert-nk-storage"]
    assert [sum(total[key] for total in upper) for key in ("originalSites", "adapterSites", "legacySites")] == [
        104, 52, 52
    ]
    display = handoff.read_text()
    assert "成功152／失敗0／エラー0／skip0／未実行0" in display
    assert "担当者の受領確認は未記録" in display
    out = E / v["run"]
    out.mkdir()
    result = dict(
        actualExit=0, source=current, candidateProductionSource=candidate, lastQualifiedCore=qualified,
        wbs="WBS-F02-a", criterion="SYS-005", originalOwnerGroups=len(by_path), originalUpper=104,
        migratedUpperBefore=48, migratedUpperCurrent=52, remainingUpper=52,
        unchangedDirectStorageSites=3, sharedAdapterBridge=old_roster["bridgeCount"],
        moduleBoundaries=counters, sourcePathsReconciled=changes, runReplayed=0, newProductTests=0,
        scopedExistingCurrentTests=8, oldTestsAdded=0, fullSixBuild=False, wholeRuntime=False,
        whole451=False, officialDelta=0, recipientsAcknowledged=False,
        oracleReferences=v["oracleReferences"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(dict(migratedUpper=52, remainingUpper=52, directStorage=3, newFormal=0))


if __name__ == "__main__":
    main()
