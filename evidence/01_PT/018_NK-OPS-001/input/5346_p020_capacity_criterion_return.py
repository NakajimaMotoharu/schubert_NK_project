"""Return the current single-run tool proof to its exact WBS row and F04 handoff."""

import json
from pathlib import Path
import re
import runpy


UPPER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, PLAN, COMMON = (UPPER[k] for k in ("EVIDENCE", "PLAN", "COMMON"))
KEY = "currentP020RealFileStoreSingle209PG40400"


def main():
    read, pin, dump, sha = UPPER["read"], *(COMMON[k] for k in ("pin", "dump", "sha"))
    begin = read(next(PLAN.glob("833_*")))
    v = begin["values"]
    refs = v["oracleReferences"]
    assert all(pin(Path(ref["path"])) == ref for ref in refs)
    _, run, post, static, old_host, inventory, current, handoff, execution_wbs = (
        Path(row["path"]) for row in refs)
    runtime, proof, style, history = map(read, (run, post, static, old_host))
    assert runtime["actualExit"] == proof["actualExit"] == style["actualExit"] == 0
    assert proof["productionCore"] == v["productionCoreMain"]
    assert proof["tests"] == 209 and proof["requiredExistingTests"] == 208
    assert proof["toolFour100"] and proof["manualCoverageExclusions"] == 0 and not proof["oldExecMerged"]
    assert not proof["rawMissedMethods"] and not proof["livePreflightTwoMissingMethodsRemaining"]
    assert style["correctedCheckstyleExit"] == style["formatExit"] == style["pmdApplicable"] == 0
    assert style["pmdRaw"] == 1 and not style["sourceByteChanged"]
    assert runtime["admission"] == proof["cwdAdmission"] and history["actualExit"] == 0
    rows = [row.split("\t") for row in execution_wbs.read_text().splitlines() if row]
    selected, = [row for row in rows if row[2] == "WBS-P020-01.01/2-b"]
    finish, = [row for row in rows if row[2] == "閉/WBS-P020-01.01"]
    assert selected[0] == "116" and selected[5] == "1.5" and finish[0] == "157"
    record = dict(wbsRow=selected[2], rank=int(selected[0]), originalPlanPricePp=float(selected[5]),
                  linkedRows=["WBS-P020-01.02/2", "WBS-F04"],
                  originalGateNames=["WBS-P020-01.01/criterion/quality", "閉/WBS-P020-01.01"],
                  toolEvidenceStatus="LOCAL_TOOL_SAME_SESSION_DELIVERABLE_PROVED",
                  formalAcceptanceStatus="WAITING_FOR_PRODUCT_DEPENDENCIES_AND_REMAINING_CRITERIA",
                  sourceTool=proof["exactToolSource"], givenProductionCore=proof["productionCore"],
                  exact209Runtime=refs[1], independentFour100=refs[2], selectedStatic=refs[3],
                  currentHostBoot=runtime["admission"]["boot"], currentHostBytes=runtime["admission"]["freeBytes"],
                  localCases=209, measuredToolCounters=proof["rawCounters"], newProductTests=0,
                  origPriceRetainedNoCompletionCharge=True, completedOriginalPricePp=0, formalDelta=0,
                  unresolved=["P020.01 /2-c", "F02/F03 all six and full quality",
                              "actual Current/NK and remaining P020 children", "451"])
    original = inventory.read_text()
    old = json.loads(original)
    assert KEY not in old and original.startswith("{\n")
    entry = json.dumps({KEY: record}, ensure_ascii=False, indent=2)[2:-2]
    replaced = "{\n" + entry + ",\n" + original[2:]
    assert json.loads(replaced) == {KEY: record, **old}
    before = current.read_text()
    assert read(current)["inventorySha256"] == pin(inventory)["sha256"]
    digest = sha(replaced.encode())
    after, num = re.subn(r'("inventorySha256": ")[0-9a-f]{64}(")',
                         lambda x: x[1] + digest + x[2], before)
    assert num == 1
    previous_text = handoff.read_text()
    note = ("\n2026-11-20 JST F04追補。harukaの新boot・mini専有0700領域で、実空き"
            f"{record['currentHostBytes']:,} byteを開始時に確認。通常FileStore一件を比較器208と同一runで209成功、"
            "工具四指標全到達。PG40398が独立根拠。旧PG40160は歴史。実Unit・DB分離・全451、担当受領は未確認。"
            " [PG40398 manifest](../../../../evidence/01_PT/018_NK-OPS-001/evidence/"
            "PG40398-p020-single-session-filestore-independent-v1/manifest.json)\n")
    assert note not in previous_text
    inventory.write_text(replaced)
    current.write_text(after)
    handoff.write_text(previous_text + note)
    out = STORE / v["run"]
    out.mkdir()
    data = dict(actualExit=0, source=v["source"], productionCore=v["productionCoreMain"],
                sourceEvidence=refs, originalOutcome=record, inventoryAfter=pin(inventory),
                snapshotAfter=pin(current), handoffAfter=pin(handoff), sourceRunsCombined=False,
                productTestsExecuted=0, previousTestsReplayed=0, formalDelta=0, whole451Accepted=False,
                terminalAtUTC=COMMON["timestamp"]())
    dump(out / "manifest.json", data)
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
