"""Bind three migrated calls and the existing ordering co-test to the current artifacts."""

import json
from pathlib import Path
import re
import runpy


UPPER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, PLAN, COMMON = (UPPER[key] for key in ("EVIDENCE", "PLAN", "COMMON"))
KEY = "currentG08PublicCheckpointCallsPG40388"


def main():
    read, pin, dump = UPPER["read"], COMMON["pin"], COMMON["dump"]
    start = read(next(PLAN.glob("821_*")))
    group = start["values"]
    refs = group["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in refs)
    ref_paths = [Path(ref["path"]) for ref in refs]
    _, unit, jars, typed, history, inventory, snapshot, handoff = ref_paths
    candidate, product, static = map(read, (unit, jars, typed))
    core = group["productionCoreMain"]
    assert candidate["productionCore"] == product["productionCore"] == static["productionCore"] == core
    assert candidate["firstPass"] == 4 and candidate["newAdapterCalls"] == 3
    assert candidate["actualExit"] == product["actualExit"] == static["actualExit"] == 0
    assert candidate["newProductCases"] == candidate["newFormalAcceptance"] == static["formalDelta"] == 0
    fixture = "dev.codex.schubert.nk.bootstrap.CheckpointFatalBoundaryTest"
    all_previous = {r["name"] for r in read(history)["cases"]
                    if r["classname"] == fixture and r["result"] == "PASS"}
    current = {
        "ncheckFatal001ConstructorKeepsSameErrorFromSourceAndInvocation()":
            ("NCHECK-FATAL-001", "FixedNativeCoverageCheckpoint$PublicAgent.<init>"),
        "ncheckFatal002BothStringGettersKeepSameGraphErrorAndFixedNonfatal()":
            ("NCHECK-FATAL-002", "FixedNativeCoverageCheckpoint$PublicAgent.string"),
        "ncheckFatal003DataGetterKeepsSameGraphErrorAndNeverRequestsReset()":
            ("NCHECK-FATAL-003", "FixedNativeCoverageCheckpoint$PublicAgent.executionDataWithoutReset"),
        "ncheckClosing004FixedPointValuesEarlyConsumptionAndNormalClosing()":
            ("existing exact display name", "FixedNativeCoverageCheckpoint.capture"),
    }
    assert set(current) == set(candidate["cases"]) == all_previous
    record = dict(productionCore=core, measuredTestSource=candidate["source"], originalOwner="WBS-P018-08",
                  secondaryScopes=["WBS-F02-a", "WBS-F03/2-2"], design=["SS354", "451", "SSC-461"],
                  bug="BUG-3233", testExisting=4, newProductCases=0, migratedCalls=3,
                  tests=[dict(selector=fixture + "#" + name, testId=test, method=method,
                              purpose="unchanged ordering co-test" if name.startswith("ncheckClosing")
                              else "migrated call with existing independent oracle")
                         for name, (test, method) in current.items()],
                  currentProduct=pin(unit), currentJar=pin(jars), currentSpotBugs=pin(typed),
                  rawCoverage=candidate["rawCoverage"], mergedCoverageRuns=False,
                  plannedCompletionPricePp=0, formalAdded=0,
                  stillOpen=["Actual current native actor/session and full physical CRC", "451",
                             "All P018-08 children and F02/F03 ending dependencies"])
    original = inventory.read_text()
    parsed = json.loads(original)
    assert KEY not in parsed and original.startswith("{\n")
    prior_snapshot = snapshot.read_text()
    assert read(snapshot)["inventorySha256"] == pin(inventory)["sha256"]
    entry = json.dumps({KEY: record}, ensure_ascii=False, indent=2)[2:-2]
    next_inventory = "{\n" + entry + ",\n" + original[2:]
    assert json.loads(next_inventory) == {KEY: record, **parsed}
    next_hash = COMMON["sha"](next_inventory.encode())
    next_snapshot, matches = re.subn(
        r'("inventorySha256": ")[0-9a-f]{64}(")',
        lambda match: match[1] + next_hash + match[2], prior_snapshot)
    assert matches == 1
    pending = handoff.read_text()
    handoff_note = (
        f"\n2026-11-20 JST 追補。現Core `{core}` のF02は4 JAR・1,102物理、"
        "PublicAgent一差・上位例外移管48/104。PG40378の4試験、PG40382のbyteと依存辺、"
        "PG40386のSpotBugs新1・既9物理一致を確認。F03の広域PG40366は終了2、"
        "Prometheusの1欠落はPG40372で是正、保留Root 9は残る。P018-08の実nativeと同source全451、"
        "F02/F03全六、C02実Invocation・担当受領は未確認。"
        " [PG40386 manifest](../../../../evidence/01_PT/018_NK-OPS-001/evidence/"
        "PG40386-f03-public-checkpoint-typed-independent-v1/manifest.json)\n"
    )
    assert handoff_note not in pending
    inventory.write_text(next_inventory)
    snapshot.write_text(next_snapshot)
    handoff.write_text(pending + handoff_note)
    out = STORE / group["run"]
    out.mkdir()
    data = dict(actualExit=0, source=group["source"], productionCore=core, startEvent=start["eventId"],
                trace=record, inventoryBefore=refs[5], inventoryAfter=pin(inventory),
                snapshotBefore=refs[6], snapshotAfter=pin(snapshot), handoffBefore=refs[7],
                handoffAfter=pin(handoff), testsActuallyRun=0, mergedCoverageRuns=False,
                formalScopesChanged=0, whole451Accepted=False, terminalAtUTC=COMMON["timestamp"]())
    dump(out / "manifest.json", data)
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
