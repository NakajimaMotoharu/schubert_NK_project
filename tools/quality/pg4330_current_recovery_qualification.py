"""Freeze current11 tool tests, exact inspected driver and prepared independent post, all host/emitted static0."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check,checkPath
import pg4316_current_failed_dispatch as driver
import pg4312_current_failed_owned_stage as stage
import pg4322_current_post_profile_compile as profile
import pg4324_current_failed_post as post
from pg1446_current_cold_stage import W

SLOT='pg4330-current-recovery-qualification-v1'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(['python3','-B','-m','unittest','pg4312_current_failed_owned_sources_test','pg4316_current_failed_dispatch_test','pg4324_current_failed_post_test','pg4328_current_failed_recover_test','-v'],capture_output=True)
    log=r.stdout+r.stderr;(out/'host-tests.log').write_bytes(log)
    if r.returncode or b'Ran 11 tests'not in log or not log.rstrip().endswith(b'OK'):raise ValueError('all current11 FES0 required')
    generated={'current-recovery-compile':stage.payload(),'current-post-compile':profile.payload(),'driver':driver.payload(),'post':post.payload()}
    paths=sorted(p for pattern in ['pg431*.py','pg432*.py','pg4330*.py']for p in Path('tools/quality').glob(pattern))
    if sum(checkPath(str(p))for p in paths)+sum(check(raw,'<full current '+name+'>')for name,raw in generated.items()):raise ValueError('all host and full emitted static0 required')
    actual=json.loads((W/(driver.SLOT+'-inspect')/'manifest.safe.json').read_bytes())
    dh=hashlib.sha256(generated['driver'].encode()).hexdigest();ph=hashlib.sha256(generated['post'].encode()).hexdigest()
    if actual['actualExit']!=0 or actual['payloadSha256']!=dh or actual['result']['newScopeNormalClose']is not True:raise ValueError('same actual normal inspect first')
    if (driver.ARTIFACT/'dispatch.private.py').read_bytes()!=generated['driver'].encode()or(post.ARTIFACT/'post.private.py').read_bytes()!=generated['post'].encode():raise ValueError('same frozen artifacts first')
    v={'actualExit':0,'source':driver.role.SOURCE,'toolTests':11,'failures':0,'errors':0,'skipped':0,'staticFindings':0,'driverSha256':dh,'postSha256':ph,
       'hostSha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'emittedSha256':{n:hashlib.sha256(raw.encode()).hexdigest()for n,raw in generated.items()},
       'logSha256':hashlib.sha256(log).hexdigest(),'actualInspectNormal':True,'recoveryIssued':False,'postRun':False,'productionPtAdded':0,'formalAccepted':False}
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return 0


if __name__=='__main__':raise SystemExit(main())
