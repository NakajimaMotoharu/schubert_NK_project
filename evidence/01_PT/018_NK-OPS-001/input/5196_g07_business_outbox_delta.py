"""Reuse the checked public scanner for the bounded immutable business Outbox delta."""
from importlib.util import module_from_spec, spec_from_file_location
import os
from pathlib import Path
import sys

ENTRY = Path(__file__).resolve()
B = Path('evidence/01_PT/018_NK-OPS-001')
E = B / 'evidence'
OUT = E / 'PG39660-g07-business-outbox-four-module-public-delta-v1'
START = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/476_G07業務Outboxと引渡し差分開始.json')
TEMP = Path('/dev/shm') / f'schubert-nk-pg39660-{os.getuid()}'
RETAIN = Path.cwd().parent / 'pgpt-runs/PG379' / OUT.name.lower()


def load(name, path):
    spec = spec_from_file_location(name, ENTRY.with_name(path))
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
    wrapper = configure(load('g07_scan_base', '5180_g07_jdbc_metrics_delta.py'))
    wrapper.stage_scan()


if __name__ == '__main__':
    if sys.argv[1:] != ['scan']:
        raise SystemExit('exact scan phase required')
    scan()
