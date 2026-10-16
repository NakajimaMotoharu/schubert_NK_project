"""Final host/emitted ABI and frozen artifact closure; no VM/service operation."""
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
import pg4104_failed_done_owned_dispatch as dispatch
import pg4148_failed_done_independent_post as post

ROOT=Path(__file__).resolve().parents[2]
MODULES=['pg4104_failed_done_owned_dispatch_test','pg4102_failed_done_recovery_protocol_test',
 'pg4086_failed_done_recovery_contract_test','pg4094_failed_done_nine_attribute_inspection_test',
 'pg4084_recovery_inspection_test','pg4074_failed_done_parent_contract_test','pg4078_ordinary_actor_policy_test',
 'pg4122_fixed_terminal_native_contract_test','pg4132_signed_phase_invariant_test',
 'pg1026_cold_observation_contract_test','pg4138_independent_revoked_epoch_test',
 'pg4148_failed_done_independent_post_test','pg4152_exact_failed_done_recover_test']


def main():
    os.umask(0o077);out=W/'pg4154-final-recovery-abi-v1';out.mkdir()
    command=[sys.executable,'-B','-m','unittest',*MODULES]
    r=subprocess.run(command,capture_output=True,timeout=60,cwd=ROOT);log=r.stdout+r.stderr;(out/'host-abi.log').write_bytes(log)
    count=re.search(rb'Ran ([0-9]+) tests? in ',log)
    if r.returncode!=0 or count is None:raise ValueError('final host ABI not successful')
    files=sorted({p for pattern in ['pg4086_*.py','pg4088_*.py','pg409[0468]_*.py','pg410[246]_*.py','pg411[26]_*.py','pg412[0248]_*.py','pg413[248]_*.py','pg414[248]_*.py','pg415[024]_*.py']for p in (ROOT/'tools/quality').glob(pattern)})
    findings=sum(checkPath(str(p))for p in files)+check(dispatch.payload(),'<complete final dispatch>')+check(post.payload(),'<complete independent post>')
    if findings:raise ValueError('host/emitted static closure failed')
    ds=hashlib.sha256(dispatch.payload().encode()).hexdigest();ps=hashlib.sha256(post.payload().encode()).hexdigest()
    if ds!='5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3':raise ValueError('qualified dispatch changed')
    frozen=W/'pg4150-failed-done-post-artifact-v1/post.private.py'
    if hashlib.sha256(frozen.read_bytes()).hexdigest()!=ps:raise ValueError('prepared independent post changed')
    value={'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
      'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'hostToolTests':int(count[1]),
      'logSha256':hashlib.sha256(log).hexdigest(),'staticFindings':findings,'hostStaticFiles':len(files),
      'dispatchSha256':ds,'postSha256':ps,'toolSourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files},
      'productionPtAdded':0,'oldParentNormal':False,'formalAccepted':False,'stateChangingActions':0}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in {'command','toolSourceHashes'}}));return 0


if __name__=='__main__':raise SystemExit(main())
