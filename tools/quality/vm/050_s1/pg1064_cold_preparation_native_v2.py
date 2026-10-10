"""New-only corrected stage/prepare, never dispatch old1039 reservation again."""
import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from pg1039_cold_preparation_native import source as previous

HERE=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source():
    raw=previous()
    for old,new in [('pg1038-cold-preparation-frozen-v1.safe.json','pg1063-cold-preparation-frozen-v2.safe.json'),
                    ('pg1037-cold-tools-v1','pg1062-cold-tools-v1'),
                    ('Pg1037ColdOwnedPreparation','Pg1062ColdOwnedPreparation'),
                    ('pg1039-','pg1064-'),('PG1039_','PG1064_')]:
        if old not in raw:raise ValueError('fixed v2 transport profile refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


def main():
    if sys.argv[1:]not in (['stage'],['prepare']):raise ValueError('fixed stage or prepare required')
    base=W/('pg1064-'+sys.argv[1]+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ('.begin.safe.json','.private.log','.exit','.safe.json')):
        raise ValueError('existing reservation cannot be replayed')
    try:
        exec(compile(source(),'<PG1064 fixed corrected cold preparation>','exec'),{'__file__':str(HERE/'pg1064_cold_preparation_native_v2.py'),'__name__':'__main__'})
    except Exception as failure:
        code=failure.returncode if isinstance(failure,subprocess.CalledProcessError)else 1
        value={'action':sys.argv[1],'actualExit':code,'failureType':type(failure).__name__,
               'failureDiagnosticsRedacted':True,'fullColdPreparationAccepted':False,'formalAccepted':False}
        for suffix,data in (('.exit',(str(code)+'\n').encode()),('.safe.json',json.dumps(value,sort_keys=True).encode())):
            p=Path(str(base)+suffix)
            if not p.exists():
                with p.open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
        print(json.dumps(value));raise SystemExit(code)


if __name__=='__main__':
    main()
