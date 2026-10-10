"""New-only immutable stage and one SSC256 owned recovery, never replay start."""
import ast
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from pg1025_cold_owned_native import source as previous

HERE = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source():
    raw = previous()
    changes = [("('stage','verify')", "('stage','recover')"),
               ('pg1024-cold-readback-frozen-v1.safe.json', 'pg1138-failed-recovery-frozen-v3.safe.json'),
               ('pg1023-cold-tools-v1', 'pg1134-issued-api-tools-v3'),
               ('pg1025-fixed-stage-v1', 'pg1139-fixed-stage-v1'),
               ("'pg1025-'+action+'-v1'", "'pg1139-'+action+'-v1'"),
               ('pg1025-stage-v1.exit', 'pg1139-stage-v1.exit'),
               ('Pg1023ColdOwnedReadbackTest', 'Pg1134SingleApiIntentTest'),
               ('Pg1023ColdOwnedReadback', 'Pg1134SingleApiRecovery'),
               ('0.1.0-PG932', '0.1.0-PG1068'),
               ('PG1025_IMMUTABLE_STAGE', 'PG1139_IMMUTABLE_STAGE')]
    for old, new in changes:
        if old not in raw: raise ValueError('fixed recovery transport binding refused')
        raw = raw.replace(old, new)
    raw = raw.replace("commands=[(SSH+[prefix+'Pg1134SingleApiIntentTest'],None),(SSH+[prefix+'Pg1134SingleApiRecovery '+action],None)]",
                      "commands=[(SSH+[prefix+'Pg1134SingleApiRecovery '+action],None)]")
    if "prefix+'Pg1134SingleApiIntentTest'" in raw: raise ValueError('host fixture must not run as VM operator')
    raw = raw.replace("'genuineParentAccepted':False,'readbackOnly':True,'fullColdPreparationAccepted':False",
                      "'genuineParentAccepted':False,'readbackOnly':False,'finiteRecoveryAccepted':action=='recover'and code==0")
    marker = "target=W/'pg1134-issued-api-tools-v3';files=frozen['fileHashes']"
    if raw.count(marker) != 1: raise ValueError('fixed frozen source assertion refused')
    raw = raw.replace(marker, "assert frozen['productionSource']=='d5b00104280028d9ea81b44c1d1c805f3c2861ed'and len(frozen['phases'])==4 and all(p['actualExit']==0 for p in frozen['phases'])\n    " + marker)
    raw = raw.replace("'readbackOnly':True,'state':'RESERVED_NOT_ACCEPTED'", "'readbackOnly':False,'finiteRecoveryPlanned':action=='recover','state':'RESERVED_NOT_ACCEPTED'")
    old = "with tarfile.open(archive,'r:')as tar:\n seen=set()"
    if raw.count(old) != 1: raise ValueError('fixed staged package tree insertion refused')
    raw = raw.replace(old, "directories={p.as_posix()for name in FILES for p in pathlib.PurePosixPath(name).parents if p.as_posix()!='.'}\nassert all(not pathlib.PurePosixPath(name).is_absolute()and '..'not in pathlib.PurePosixPath(name).parts for name in FILES)\nwith tarfile.open(archive,'r:')as tar:\n seen=set()")
    raw = raw.replace("(m.isdir()and p.as_posix()=='.'or m.isfile()and len(p.parts)==1)", "(m.isdir()and p.as_posix()in directories|{'.'}or m.isfile()and p.as_posix()in FILES)")
    raw = raw.replace(" root.mkdir(mode=0o700);tar.extractall(root,filter='data')", " assert seen==set(FILES)|directories|{'.'}\n root.mkdir(mode=0o700);tar.extractall(root,filter='data')")
    raw = raw.replace("assert {p.name for p in root.iterdir()}==set(FILES)|{'payload-sha256.json'}\nfor f in root.iterdir():\n s=f.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1;os.chown(f,0,0);os.chmod(f,0o400)\n with f.open('rb')as stream:os.fsync(stream.fileno())",
                      "assert {p.relative_to(root).as_posix()for p in root.rglob('*')}==set(FILES)|directories\nfor f in root.rglob('*'):\n s=f.lstat();assert not f.is_symlink();os.chown(f,0,0)\n if f.is_dir():\n  assert stat.S_ISDIR(s.st_mode);os.chmod(f,0o700)\n else:\n  assert stat.S_ISREG(s.st_mode)and s.st_nlink==1;os.chmod(f,0o400)\n  with f.open('rb')as stream:os.fsync(stream.fileno())")
    raw = raw.replace("assert json.loads((root/'payload-sha256.json').read_text())==FILES\n", '')
    ast.parse(raw); return raw


def main():
    if sys.argv[1:] not in (['stage'], ['recover']): raise ValueError('fixed stage/recover action required')
    base = W / ('pg1139-' + sys.argv[1] + '-v1')
    if any(Path(str(base) + suffix).exists() for suffix in ('.begin.safe.json', '.private.log', '.exit', '.safe.json')):
        raise ValueError('existing reservation cannot be replayed')
    try:
        exec(compile(source(), '<PG1139 immutable current failed recovery>', 'exec'), {'__file__': str(HERE / 'pg1139_failed_recovery_native.py'), '__name__': '__main__'})
    except Exception as failure:
        code = failure.returncode if isinstance(failure, subprocess.CalledProcessError) else 1
        value = dict(action=sys.argv[1], actualExit=code, failureType=type(failure).__name__,
                     completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     failureDiagnosticsRedacted=True, finiteRecoveryAccepted=False, formalAccepted=False)
        for suffix, data in [('.exit', (str(code) + '\n').encode()), ('.safe.json', json.dumps(value, sort_keys=True).encode())]:
            p = Path(str(base) + suffix)
            if not p.exists():
                with p.open('xb') as f: os.fchmod(f.fileno(), 0o600); f.write(data); f.flush(); os.fsync(f.fileno())
        print(json.dumps(value)); raise SystemExit(code)


if __name__ == '__main__': main()
