"""New-only immutable stage/owned readback. No execute/start/permit/mount/namespace action."""
import ast
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from pg986_current_bootstrap_native import source as previous

R=Path(__file__).resolve().parent

def source():
    raw=previous()
    begin="    assert(W/'pg963-stop-v1.exit')";end="    frozen=json.loads"
    assert raw.count(begin)==raw.count(end)==1
    raw=raw[:raw.index(begin)]+raw[raw.index(end):]
    for a,b in (
      ("('stage','verify','execute')","('stage','verify')"),
      ('pg983-frozen-v3.safe.json','pg1024-cold-readback-frozen-v1.safe.json'),
      ('pg983-bootstrap-tools-v3','pg1023-cold-tools-v1'),
      ('pg983-fixed-stage-v3','pg1025-fixed-stage-v1'),
      ("'pg983-'+action+'-v3'","'pg1025-'+action+'-v1'"),
      ('pg983-stage-v3.exit','pg1025-stage-v1.exit'),
      ('Pg983BootstrapArgumentTest','Pg1023ColdOwnedReadbackTest'),
      ('Pg983BootstrapExisting','Pg1023ColdOwnedReadback'),
      ('cc9ed874-7f4f-450e-a188-8de1e42c8441','cbca8738-3b24-4090-b77c-bf029677cdd6'),
      ('PG841_IMMUTABLE_STAGE','PG1025_IMMUTABLE_STAGE'),
      ("'genuineParentAccepted':True","'genuineParentAccepted':False,'readbackOnly':True,'fullColdPreparationAccepted':False")):
        assert a in raw,a;raw=raw.replace(a,b)
    marker="    if action=='stage':\n";assert raw.count(marker)==1
    reservation="""    begin_record={'action':action,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
      'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozenSha256':hashlib.sha256((W/'pg1024-cold-readback-frozen-v1.safe.json').read_bytes()).hexdigest(),
      'boot':'cbca8738-3b24-4090-b77c-bf029677cdd6','readbackOnly':True,'state':'RESERVED_NOT_ACCEPTED'}
    with Path(str(base)+'.begin.safe.json').open('x')as f:json.dump(begin_record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
"""
    raw=raw.replace(marker,reservation+marker)
    # BUG1016: this task may remain in UNKNOWN while the host legitimately moves
    # forward. Completion HEAD is not the dispatch/source identity.
    source_marker="'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()"
    assert raw.count(source_marker)==2
    first=raw.index(source_marker);last=raw.rindex(source_marker)
    assert last>first
    raw=raw[:last]+raw[last:].replace(source_marker,"'operatorSource':begin_record['operatorSource']",1)
    assert 'execute'not in raw and 'pg983-'not in raw
    ast.parse(raw);return raw

if __name__=='__main__':
    assert sys.argv[1:]in (['stage'],['verify'])
    base=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')/('pg1025-'+sys.argv[1]+'-v1')
    # Reject re-entry before the failure wrapper: never publish an exit over a live reservation.
    assert not any(Path(str(base)+suffix).exists()for suffix in ('.begin.safe.json','.private.log','.exit','.safe.json'))
    try:
        exec(compile(source(),'<PG1025 completed-cold owned readback>','exec'),{'__file__':str(R/'pg1025_cold_owned_native.py'),'__name__':'__main__'})
    except Exception as failure:
        code=failure.returncode if isinstance(failure,subprocess.CalledProcessError)else 1
        record={'action':sys.argv[1],'actualExit':code,'failureType':type(failure).__name__,
          'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'failureDiagnosticsRedacted':True,
          'readbackOnly':True,'fullColdPreparationAccepted':False,'formalAccepted':False,
          'failedSubcommandExit':code if isinstance(failure,subprocess.CalledProcessError)else None}
        for suffix,value in (('.exit',(str(code)+'\n').encode()),('.safe.json',json.dumps(record,sort_keys=True).encode())):
            p=Path(str(base)+suffix)
            if not p.exists():
                with p.open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(value);f.flush();os.fsync(f.fileno())
        print(json.dumps(record));raise SystemExit(code)
