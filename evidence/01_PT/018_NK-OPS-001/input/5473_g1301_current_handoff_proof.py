"""Fix the four-owner handoff receipts for the current production candidate."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
group = json.loads(next(plan.glob("1303_*")).read_bytes())
ctx = group["values"]
inputs = ctx["oracleReferences"][1:]
assert len(inputs) == 6
assert all(pin(Path(item["path"])) == item for item in inputs)
batch, style, typed, original, unit, filesystem = (json.loads(Path(row["path"]).read_bytes()) for row in inputs)
core = ctx["productionCoreMain"]
assert batch["source"] == style["source"] == typed["core"] == core
assert batch["approvedSingleClassComparison"]["matchesIndependentTypedAndScopedPt"]
assert style["currentTest"]["eligibleCheckstyle"] == 1119 and style["currentTest"]["unresolvedHeld"] == 32
assert typed["reported"] == 27
assert original["technical"]["tests"] == 152 and original["technical"]["normalPtExecuted"]
assert all(original["technical"][key] == 0 for key in ("failed", "errors", "skipped"))
handoff = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/760_11月25日四担当の引渡し現行差分.md")
new_section = handoff.read_text().split("## 2026-11-20 現候補の引渡し", 1)[0]
assert core in new_section and all(f"| {owner} |" in new_section for owner in ("F02", "F03", "C02", "F04"))
assert all(Path(item["path"]).parent.name in new_section for item in inputs)
out = Path("evidence/01_PT/018_NK-OPS-001/evidence") / ctx["run"]
out.mkdir()
output = dict(actualExit=0, core=core, fourOwnerReceipts=inputs, handoff=pin(handoff),
              historicalSsc447OriginalSource=original["productionCoreMain"], historicalSsc447Tests=152,
              currentOwnerAcknowledgementsObserved=None, actualNewExternalObservations=0, productTestsRerun=0,
              whole451=False, officialAcceptanceDelta=0, startEvent=group["eventId"],
              terminalAtUTC=datetime.now(timezone.utc).isoformat())
path = out / "manifest.json"
path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
print(pin(path))
