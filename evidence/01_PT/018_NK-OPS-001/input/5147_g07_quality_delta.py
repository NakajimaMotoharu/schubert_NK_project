"""Run the established scanner on the immutable published quality delta."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
OUT = EVIDENCE / "PG39430-g07-quality-published-delta-v1"
WORK = Path.cwd().parent / "pgpt-runs/PG379" / OUT.name.lower()
START = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/444_G07最近の品質成果公開増分開始.json")
STAGES = {
    "scan": "5109_g07_committed_delta_scan.py",
    "ground": "5110_g07_committed_delta_ground.py",
    "bind": "5111_g07_committed_delta_bind.py",
}


def load_stage(stage):
    location = EVIDENCE.parent / "input" / STAGES[stage]
    spec = spec_from_file_location("g07_" + stage, location)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.WORK = WORK
    if stage == "scan":
        module.START = START
        module.EVIDENCE = OUT
    else:
        module.OUT = OUT
        if stage == "ground":
            module.OLD = EVIDENCE / "PG39284-g07-published-recorder-delta-v1"
    return module


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in STAGES:
        raise SystemExit("one of scan, ground, bind is required")
    load_stage(sys.argv[1]).main()
