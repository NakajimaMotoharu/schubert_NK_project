"""Apply the established redacted G07 scanner to the next immutable public range."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
INPUTS = EVIDENCE.parent / "input"
OUT = EVIDENCE / "PG39284-g07-published-recorder-delta-v1"
WORK = Path.cwd().parent / "pgpt-runs/PG379/pg39284-g07-published-recorder-delta-v1"
START = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/417_G07最近のRecorder公開差分開始.json")
PRIOR = EVIDENCE / "PG39196-g07-current-published-delta-v1"
ORIGINAL = {
    "scan": "5109_g07_committed_delta_scan.py",
    "ground": "5110_g07_committed_delta_ground.py",
    "bind": "5111_g07_committed_delta_bind.py",
}


def run(stage):
    location = INPUTS / ORIGINAL[stage]
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
            module.OLD = PRIOR
    module.main()


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ORIGINAL:
        raise SystemExit("one of scan, ground, bind is required")
    run(sys.argv[1])
