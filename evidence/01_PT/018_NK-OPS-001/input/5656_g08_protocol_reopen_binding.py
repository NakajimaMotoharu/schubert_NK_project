"""Bind the changed Protocol evidence and reconcile one original acceptance reopening."""

from datetime import datetime, timezone
import json
from pathlib import Path
import runpy


H = runpy.run_path(str(Path(__file__).with_name("5646_g08_media_compare_current.py")))
DOCS, OPS, pin, named, read, attach, git = (H[n] for n in
    ("DOCS", "OPS", "pin", "named", "read", "attach", "git"))
ITEM = "WBS-P002-01"
KEY = "currentProtocolNumericValidationPG41308"
RUN = "PG41308-g08-protocol-reopen-binding-v1"


def main():
    ctx = read(named(DOCS, "601_*/1701_*.json"))["values"]
    refs = [Path(row["path"]) for row in ctx["oracleReferences"]]
    assert list(map(pin, refs)) == ctx["oracleReferences"]
    previous, raw, quality, reopened, master = refs
    a, b, c = [read(path) for path in (raw, quality, reopened)]
    assert a["source"] == b["source"] == ctx["productionCoreMain"]
    assert Path(b["qualified"]["path"]).resolve() == raw.resolve()
    assert b["qualified"]["sha256"] == pin(raw)["sha256"]
    assert a["ordinaryTests"] == 171 and a["fullProtocol"] and a["jarPhysicalCount"] == 176
    assert a["scopeWidth"]["exactKnownWireLayoutsAffected"] is False
    assert not any(b["dependencyRuleFindings"].values()) and not b["rawPmdFindings"] and b["checkstyleFindings"] == 0
    assert c["acceptedDelta"]["reopenedIds"] == [ITEM] and not c["acceptedDelta"]["closedIds"]
    assert c["acceptedOriginal"] == 16 and c["formalSnapshotUnchanged"] == dict(tests=1964, scopes=53)
    snapshot = named(DOCS, "486_*.json")
    inventory = named(DOCS, "485_*.json")
    status = read(snapshot)
    master_rows = {t["id"]: t["acceptance"] for t in read(master)["tasks"]}
    snapshot_rows = {t["id"]: t["acceptance"] for t in status["rows"]}
    assert len(master_rows) == len(snapshot_rows) == 190 and master_rows.keys() == snapshot_rows.keys()
    assert {key for key in master_rows if master_rows[key] != snapshot_rows[key]} == {ITEM}
    assert {**master_rows[ITEM], "status": "ACCEPTED"} == snapshot_rows[ITEM]
    assert sum(row["status"] == "ACCEPTED" for row in snapshot_rows.values()) == 17
    assert sum(row["status"] == "ACCEPTED" for row in master_rows.values()) == 16
    assert all((Path(entry["path"]).is_file() and pin(Path(entry["path"]))["sha256"] == entry["sha256"])
               for entry in master_rows[ITEM]["evidence"])
    wbs = named(Path("../PMO/hourly-monitor/wbs66-20261116"), "58_*/WBS.tsv")
    rows = wbs.read_text().splitlines()
    spec = named(Path("evidence/01_PT/002_NK-PRO-002"), "105_Field*")
    result = []
    for n, leaf, source in ((295, ITEM + "/2", raw), (582, "WBS-F02-a", quality),
                            (1004, "WBS-F03/2-2", quality)):
        row = rows[n - 1].split("\t")
        assert row[0] == leaf
        result.append(dict(workId=leaf, originalWbsRow=n, originalPricePp=float(row[6]),
                           confirmedProof=pin(source), testId="PT-PRO-002-N03",
                           specification=pin(spec), currentEffect="LOCAL_QUALIFICATION_ONLY"))
    assert git("rev-parse", "origin/main").decode().strip() == ctx["canonicalDesignSource"]
    before = pin(inventory)["sha256"]
    assert status["inventorySha256"] == before
    out = OPS / RUN
    out.mkdir()
    terminal = out / "manifest.json"
    data = dict(actualExit=0, source=ctx["source"], core=ctx["productionCoreMain"],
                acceptanceDocument=pin(master), originalReopen=pin(reopened), originalWbs=pin(wbs),
                currentAccepted=16, historicalAccepted=17, reopened=[ITEM], newFormalAcceptance=0,
                stateChanges=[ITEM], other190RowsChanged=0, preservedPriorEvidence=master_rows[ITEM]["evidence"],
                originalFormalPt=1964, originalFormalPtScopes=53, bindings=result, completedCostPp=0,
                newProductTests=0, wholeG08=False, whole451=False, priorCheckpoint=pin(previous),
                terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with terminal.open("x") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    snapshot_text = snapshot.read_text()
    start = snapshot_text.index(f'      "id": "{ITEM}",')
    target = snapshot_text.index('      "acceptance": {', start)
    marker = '"status": "ACCEPTED"'
    pos = snapshot_text.index(marker, target)
    assert snapshot_text[target:pos].strip() == '"acceptance": {'
    replacement = snapshot_text[:pos] + snapshot_text[pos:].replace(marker, '"status": "RECHECK_REQUIRED"', 1)
    assert {row["id"]: row["acceptance"] for row in json.loads(replacement)["rows"]} == master_rows
    snapshot.write_text(replacement)
    binding = dict(currentCore=a["source"], acceptedActive=16, baselineAccepted=17,
                   originalReopened=[ITEM], newAccepted=0, report=pin(terminal), roles=result)
    attach(inventory, KEY, binding)
    attach(snapshot, KEY, binding)
    old = '"inventorySha256": "' + before + '"'
    new = '"inventorySha256": "' + pin(inventory)["sha256"] + '"'
    state = snapshot.read_text()
    assert state.count(old) == 1
    snapshot.write_text(state.replace(old, new, 1))
    print(pin(terminal), "190 matching acceptance records, 16 active")


if __name__ == "__main__":
    main()
