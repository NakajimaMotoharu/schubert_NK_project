"""New-only stage/prepare, preserving old1025/1035 slots and begin-source identity."""
import ast
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from pg1025_cold_owned_native import source as previous

HERE=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source():
    raw=previous()
    replacements=[("('stage','verify')","('stage','prepare')"),
      ('pg1024-cold-readback-frozen-v1.safe.json','pg1038-cold-preparation-frozen-v1.safe.json'),
      ('pg1023-cold-tools-v1','pg1037-cold-tools-v1'),
      ('pg1025-fixed-stage-v1','pg1039-fixed-stage-v1'),
      ("'pg1025-'+action+'-v1'","'pg1039-'+action+'-v1'"),
      ('pg1025-stage-v1.exit','pg1039-stage-v1.exit'),
      ('Pg1023ColdOwnedReadbackTest','Pg1037ColdOwnedPreparationTest'),
      ('Pg1023ColdOwnedReadback','Pg1037ColdOwnedPreparation'),
      ('PG1025_IMMUTABLE_STAGE','PG1039_IMMUTABLE_STAGE'),
      ("'readbackOnly':True","'readbackOnly':False,'finiteColdPreparation':True"),
      ("'fullColdPreparationAccepted':False","'fullColdPreparationAccepted':action=='prepare'and code==0"),
      ("'genuineSourceProofVerified':True","'frozenOperatorPayloadVerified':True")]
    for old,new in replacements:
        if old not in raw:raise ValueError('fixed transport profile refused')
        raw=raw.replace(old,new)
    # Begin must not reference completion's code before the subprocess exists.
    raw=raw.replace("'readbackOnly':False,'finiteColdPreparation':True,'state':'RESERVED_NOT_ACCEPTED'",
                    "'finiteColdPreparation':True,'state':'RESERVED_NOT_ACCEPTED'")
    ast.parse(raw);return raw


def main():
    if sys.argv[1:]not in (['stage'],['prepare']):raise ValueError('fixed stage or prepare required')
    base=W/('pg1039-'+sys.argv[1]+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ('.begin.safe.json','.private.log','.exit','.safe.json')):
        raise ValueError('old reservation cannot be replayed')
    try:
        exec(compile(source(),'<PG1039 fixed completed cold preparation>','exec'),{'__file__':str(HERE/'pg1039_cold_preparation_native.py'),'__name__':'__main__'})
    except Exception as failure:
        code=failure.returncode if isinstance(failure,subprocess.CalledProcessError)else 1
        value={'action':sys.argv[1],'actualExit':code,'failureType':type(failure).__name__,
          'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'failureDiagnosticsRedacted':True,
          'fullColdPreparationAccepted':False,'formalAccepted':False}
        for suffix,data in (('.exit',(str(code)+'\n').encode()),('.safe.json',json.dumps(value,sort_keys=True).encode())):
            p=Path(str(base)+suffix)
            if not p.exists():
                with p.open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
        print(json.dumps(value));raise SystemExit(code)


if __name__=='__main__':main()
