"""One frozen host qualification and safe read-only evidence publication. No VM actions."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from pyflakes.api import check,checkPath
from pg1446_current_cold_stage import W
from pg4154_final_recovery_abi import MODULES
from pg4176_partial_coordinator import files

ROOT=Path(__file__).resolve().parents[2]
EXTRA=['pg4162_configuration_declarations_test','pg4164_retained_pair_profile_test',
       'pg4166_partial_recovery_sources_test','pg4168_retained_pair_keeper_test',
       'pg4178_pool_bounds_test','pg4188_exact_partial_recover_test']


def main():
    os.umask(0o077);out=W/'pg4190-partial-recovery-qualification-v1';out.mkdir(mode=0o700)
    command=[sys.executable,'-B','-m','unittest',*MODULES,*EXTRA]
    result=subprocess.run(command,capture_output=True,timeout=60,cwd=ROOT)
    log=result.stdout+result.stderr;(out/'host-tests.log').write_bytes(log)
    count=re.search(rb'Ran ([0-9]+) tests? in ',log)
    if result.returncode!=0 or count is None:raise ValueError('original complete host qualification failed')
    paths=sorted(p for pattern in ['pg416*.py','pg417*.py','pg418*.py','pg4190*.py']for p in(ROOT/'tools/quality').glob(pattern))
    sources=files();findings=sum(checkPath(str(p))for p in paths)+sum(check(raw,'<'+name+'>')for name,raw in sources.items())
    if findings:raise ValueError('all host/emitted static closure required')
    value={'actualExit':0,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','hostToolTests':int(count[1]),'staticFindings':0,
           'logSha256':hashlib.sha256(log).hexdigest(),'files':{n:hashlib.sha256(raw.encode()).hexdigest()for n,raw in sources.items()},
           'toolSourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},
           'productionPtAdded':0,'old4152Normal':False,'formalAccepted':False,'stateChangingActions':0}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='toolSourceHashes'}))
    return 0


if __name__=='__main__':raise SystemExit(main())
