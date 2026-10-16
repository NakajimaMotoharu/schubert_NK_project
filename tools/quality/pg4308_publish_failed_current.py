"""Save bounded failed-current receipts and affected3 tests/static closure, no raw originals."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from pyflakes.api import check,checkPath
import pg4300_current_failed_capture as capture
import pg4302_current_failed_parent_read as parent
import pg4306_current_failed_authority_read as authority
from pg1446_current_cold_stage import W

SLOT='PG4308-current-failed-authentication-v1'


def main():
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT;out.mkdir();files={}
    r=subprocess.run(['python3','-B','-m','unittest','pg4304_current_failed_parent_contract_test','-v'],capture_output=True)
    log=r.stdout+r.stderr
    if r.returncode or b'Ran 3 tests'not in log or not log.rstrip().endswith(b'OK'):raise ValueError('all affected failed-parent3 FES0 required')
    paths=sorted(Path('tools/quality').glob('pg430*.py'))
    emitted={n:p.payload()for n,p in [('capture',capture),('parent',parent),('authority',authority)]}
    if sum(checkPath(str(p))for p in paths)+sum(check(raw,'<current failed '+name+'>')for name,raw in emitted.items()):raise ValueError('all host/full emitted static0 required')
    p=out/'host-tests.log';p.write_bytes(log);files[p.name]=hashlib.sha256(log).hexdigest()
    for slot in [capture.SLOT,parent.SLOT,authority.SLOT]:
        raw=(W/slot/'manifest.safe.json').read_bytes();v=json.loads(raw)
        if v['actualExit']!=0:raise ValueError('actual readonly receipts0 required')
        v['originalManifestSha256']=hashlib.sha256(raw).hexdigest();p=out/(slot+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    observer=W/'pg4220-watch-v1.safe.json'
    if observer.exists():
        p=out/'original-observer.safe.json';p.write_bytes(observer.read_bytes());files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    v={'source':parent.SOURCE,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'toolTests':3,'failures':0,'errors':0,'skipped':0,
       'hostSha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'emittedSha256':{n:hashlib.sha256(r.encode()).hexdigest()for n,r in emitted.items()},
       'parentNormal':False,'genuineRootDone':False,'normalAcceptanceNotRun':True,'recoveryNotIssued':True,'productionPtAdded':0,'formalAccepted':False}
    p=out/'manifest.json';p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
