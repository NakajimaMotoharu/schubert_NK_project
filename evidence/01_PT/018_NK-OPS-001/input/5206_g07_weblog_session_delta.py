"""Run the fixed public scanner once for the pushed WebLog/SESSION/CHR interval."""
from importlib.util import module_from_spec, spec_from_file_location
import os
from pathlib import Path
import sys

ENTRY = Path(__file__).resolve()
BASE = Path('evidence/01_PT/018_NK-OPS-001')
EVIDENCE = BASE / 'evidence'
GROUP = EVIDENCE / 'PG39730-g07-weblog-session-and-comparator-public-delta-v1'
OUT = GROUP / 'scan'
START = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/'
             '487_G07WebLog・SESSION・比較公開差分開始.json')
TEMP = Path('/dev/shm') / f'schubert-nk-pg39730-{os.getuid()}'
RETAIN = Path.cwd().parent / 'pgpt-runs/PG379' / GROUP.name.lower()


def load(name, filename):
    spec = spec_from_file_location(name, ENTRY.with_name(filename))
    instance = module_from_spec(spec)
    spec.loader.exec_module(instance)
    return instance


def configure(wrapper):
    wrapper.OUT = OUT
    wrapper.START = START
    wrapper.TEMP = TEMP
    wrapper.RETAIN = RETAIN
    return wrapper


def scan():
    wrapper = configure(load('g07_scan_weblog_base', '5180_g07_jdbc_metrics_delta.py'))
    wrapper.stage_scan()


if __name__ == '__main__':
    if sys.argv[1:] != ['scan']:
        raise SystemExit('exact scan phase required')
    scan()
