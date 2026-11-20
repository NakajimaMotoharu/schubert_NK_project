"""Bind selected current results to WBS and the November handoff without changing acceptance."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import runpy
import subprocess


ROOT = Path(__file__).resolve().parents[4]
PLAN = next((ROOT / "documents/400_PGPT/470_PMO").glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
KEY = "currentG08FormWireAndQualityPG40758"


def read(path):
    return json.loads(Path(path).read_bytes())


def pin(path):
    p = Path(path)
    return {"path": str(path), "sha256": sha256(p.read_bytes()).hexdigest()}


def prepend(raw, entry):
    assert raw.startswith(b"{\n") and KEY not in json.loads(raw)
    member = json.dumps({KEY: entry}, ensure_ascii=False, indent=2)[2:-2].encode()
    return b"{\n" + member + b",\n" + raw[2:]


def main():
    start = read(next(PLAN.glob("1120_G08*")))
    v = start["values"]
    refs = start["values"]["oracleReferences"]
    assert all(pin(ref["path"]) == ref for ref in refs)
    _, ir, sr, hand, unit, calendar, deps, batch = refs
    composite, dated, graph, lineage = [read(x["path"]) for x in (unit, calendar, deps, batch)]
    core = v["productionCoreMain"]
    assert composite["sourceCore"] == dated["core"] == graph["productionCore"] == lineage["productionCore"] == core
    assert composite["actualExit"] == graph["actualExit"] == lineage["actualExit"] == 0
    assert composite["passed"] == 2 and dated["runExit"] == 1 and len(dated["observations"]) == 4
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == v["source"]
    assert not subprocess.check_output(["git", "diff", "--name-only", core, "--", "src", "pom.xml"])
    record = {
        "productionCore": core,
        "searchQuestions": {"costOwner": "WBS-P016-22", "program": "NK-WEB-002",
                            "testSpecification": "PT-QRY-HTTP001/002", "record": unit,
                            "testIds": [case["testId"] for case in composite["cases"]],
                            "newLocallyPassed": 2, "coverage": None},
        "calendarObservation": {"costOwners": ["WBS-P016-20", "WBS-P016-22"],
                                "tests": ["PT-NTF-HTTP003", "PT-QRY-HTTP003"],
                                "record": calendar, "observations": dated["observations"],
                                "pending": ["BUG-3410", "YKT-2733", "QA-060", "UIC-013", "SSC-475"],
                                "newLocallyPassed": 0},
        "F02": {"record": deps, "ownedPhysical": 1102, "apiWebBuildsMissing": True},
        "F03": {"record": batch, "mainScopeLineage": 128, "wholeProductAnalysisMissing": True},
        "formalDelta": 0, "originalRowPriceChargedPp": 0, "whole451Accepted": False,
    }
    ip, sp, hp = map(lambda item: Path(item["path"]), (ir, sr, hand))
    previous_inv, previous_snapshot = ip.read_bytes(), sp.read_bytes()
    add = prepend(previous_inv, record)
    new_hash = sha256(add).hexdigest()
    snap = prepend(previous_snapshot, record)
    snap, count = re.subn(rb'("inventorySha256": ")[0-9a-f]{64}(")',
                          lambda m: m[1] + new_hash.encode() + m[2], snap)
    assert count == 1 and json.loads(add) == {KEY: record, **json.loads(previous_inv)}
    assert json.loads(snap) == {**json.loads(previous_snapshot), KEY: record, "inventorySha256": new_hash}
    guard = runpy.run_path(str(ROOT / "evidence/01_PT/018_NK-OPS-001/input/580_wbs_inventory_reference_guard.py"))
    assert guard["validate_bytes"](previous_inv, previous_snapshot)["bindingValid"]
    assert guard["validate_bytes"](add, snap)["bindingValid"]
    def link(ref):
        return f'[実行manifest]({Path(ref["path"]).resolve().relative_to(ROOT).as_posix()})'.replace(
            "(evidence/", "(../../../../evidence/", 1)
    handoff = (
        f"\n\n2026-11-20 JST追補。当製品Core `{core}`。F02の現四製品JARは"
        f"1,102 class・17,870参照を照合し、製品間の既定3方向、未宣言・未解決NK各0件。"
        f"既Storage JDBC一辺、API/Webと全実条件は残る。{link(deps)}\n\n"
        f"F03はBatchの旧対象128 Mainのうち126 sourceと270物理の同一性を確認。"
        f"現差分Expiry17件を局所判定、Cleanup48件のうち24件は未分類。元未分類12と旧対象外72も残る。"
        f"全六・全451の受入は未成立。{link(batch)}\n\n"
        "SSC447の元runとC02・F04の既引渡し資料は保存済み。今回追補の担当受領は未確認。"
        "試験再実行・正式加算・原行費用完了は各0。\n"
    ).encode()
    assert handoff not in hp.read_bytes()
    ip.write_bytes(add)
    sp.write_bytes(snap)
    hp.write_bytes(hp.read_bytes() + handoff)
    out = OPS / v["run"]
    out.mkdir()
    result = dict(actualExit=0, source=v["source"], productionCore=core,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), record=record,
                  before=refs[1:4], after=[pin(p) for p in (ip, sp, hp)],
                  runner=pin(Path(__file__)), testsRun=0, formalDelta=0, recipientAck=False)
    (out / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
