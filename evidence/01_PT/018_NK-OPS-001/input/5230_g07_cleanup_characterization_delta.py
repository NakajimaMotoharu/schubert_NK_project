"""Bind the unchanged published-delta scanner to the current exact G07 interval."""
from pathlib import Path
import json
import runpy

HERE=Path(__file__)
U=runpy.run_path(str(HERE.with_name('5216_g07_scope_build_delta.py')))
START=next(Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('509_*'))
GROUP=Path('evidence/01_PT/018_NK-OPS-001/evidence')/json.loads(START.read_bytes())['values']['run']
OUT=GROUP/'scan'
TEMP=Path(json.loads(START.read_bytes())['values']['volatileStaging'])
RETAIN=Path.cwd().parent/'pgpt-runs/PG379'/GROUP.name.lower()


def configure(module):
    module.OUT=OUT
    module.START=START
    module.TEMP=TEMP
    module.RETAIN=RETAIN
    return module


if __name__=='__main__':
    scanner=configure(U['load']('g07_cleanup_chr_base','5180_g07_jdbc_metrics_delta.py'))
    scanner.stage_scan()
