"""Scan a fixed pushed delta with private disposable projection staging and retained receipts."""
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import shutil
import sys

BASE = Path("evidence/01_PT/018_NK-OPS-001")
OUT = BASE / "evidence/PG39580-g07-published-jdbc-web-monitoring-delta-v1"
START = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/463_G07JDBC監視の公開差分開始.json")
TEMP = Path("/dev/shm") / f"schubert-nk-pg39580-{os.getuid()}"
RETAIN = Path.cwd().parent / "pgpt-runs/PG379" / OUT.name.lower()
STAGES={"scan":"5109_g07_committed_delta_scan.py","ground":"5110_g07_committed_delta_ground.py",
        "bind":"5111_g07_committed_delta_bind.py"}


def load_stage(name):
    p = BASE / "input" / STAGES[name]
    spec = spec_from_file_location("g07_" + name,p)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.WORK = TEMP
    if name=="scan":
        # This original capacity check applies to the filesystem holding the projection.
        module.ROOT = TEMP
        module.EVIDENCE = OUT
        module.START = START
    else:
        module.OUT = OUT
        if name=="ground":
            module.OLD = BASE / "evidence/PG39430-g07-quality-published-delta-v1"
    return module


def stage_scan():
    record=json.loads(START.read_bytes())
    assert Path(record["values"]["volatileStaging"]) == TEMP
    assert TEMP.parent.resolve()==TEMP.parent and TEMP.parent.is_mount()
    assert shutil.disk_usage(TEMP.parent).free>=1300*1024**2
    assert shutil.disk_usage(RETAIN.parent).free>=750*1024**2
    os.umask(0o077)
    TEMP.mkdir(mode=0o700,exist_ok=False)
    module=load_stage("scan")
    module.main()
    receipt=json.loads((OUT/"scan-terminal.json").read_bytes())
    RETAIN.mkdir(mode=0o700,exist_ok=False)
    for file, field in (("scanner-redacted.json","reportSha256"),("projection.json","projectionSha256")):
        src=TEMP/file
        content=src.read_bytes()
        assert module.digest(content)==receipt[field]
        with (RETAIN/file).open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        assert module.digest((RETAIN/file).read_bytes()) == receipt[field]


if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in STAGES:
        raise SystemExit("one of scan, ground, bind required")
    if sys.argv[1]=="scan":
        stage_scan()
    else:
        assert TEMP.is_dir() and TEMP.resolve()==TEMP and TEMP.stat().st_uid==os.getuid()
        load_stage(sys.argv[1]).main()
