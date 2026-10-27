"""Fail-closed lint-before-body for an explicitly reviewed top-level public Python entry only."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
TC=ROOT.parent/'toolchain'
HELD='tools/quality/pg9892_snapshot_key_close_witness.py'


def permitted_name(value):
    # Names rejected before any path metadata/content access. Not a permission/safety override.
    return isinstance(value,str) and value!=HELD and re.fullmatch(r'tools/quality/pg[1-9][0-9]+_[a-z0-9_]+\.py',value) is not None


def body_allowed(code):
    return type(code) is int and code==0


def main():
    if len(sys.argv)!=2 or not permitted_name(sys.argv[1]) or Path.cwd()!=ROOT:
        raise ValueError('one explicitly reviewed public top-level entry, repository cwd required')
    assert not any(permitted_name(v) for v in (HELD,'../other.py','tools/quality/vm/050_s1/pg499_runtime_retirement_test.py','tools/quality/architecture/SnapshotKeyCloseWitness.java','x;echo y'))
    assert body_allowed(0) and not any(body_allowed(v) for v in (1,2,-15,None,False,'0'))
    name=sys.argv[1]
    target=ROOT/name
    if target.is_symlink() or not target.is_file() or target.resolve()!=target:
        raise ValueError('regular canonical existing public entry required')
    before=hashlib.sha256(target.read_bytes()).hexdigest()
    env=dict(os.environ)
    env['PYTHONPATH']=os.pathsep.join(map(str,[ROOT/'tools/quality',ROOT/'tools/quality/vm/050_s1',TC/'pyflakes-3.4.0/runtime']))
    lint=subprocess.run([sys.executable,'-B','-m','pyflakes',name],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,check=False)
    if not body_allowed(lint.returncode):
        print(json.dumps(dict(checkedEntry=name,entrySha256=before,lintExit=lint.returncode,bodyStarted=False,bodyExit=None)),flush=True)
        raise SystemExit(lint.returncode or 1)
    if hashlib.sha256(target.read_bytes()).hexdigest()!=before:
        raise ValueError('entry source changed between lint and body')
    print(json.dumps(dict(checkedEntry=name,entrySha256=before,lintExit=0,bodyStarted=True)),flush=True)
    body=subprocess.run([sys.executable,'-B',name],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,check=False)
    if hashlib.sha256(target.read_bytes()).hexdigest()!=before:
        raise ValueError('entry source changed during body')
    print(json.dumps(dict(checkedEntry=name,entrySha256=before,lintExit=0,bodyStarted=True,bodyExit=body.returncode)),flush=True)
    raise SystemExit(body.returncode)


if __name__=='__main__':
    main()
