"""Publish only sanitized final read/ABI manifests; raw DB/native/journal/key artifacts stay private."""
import datetime
import hashlib
import json
import os
from pathlib import Path
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]
SLOTS=['pg4134-signed-phase-dispatch-qualification-v1-inspect','pg4142-signed-namespace-read-v1',
       'pg4144-complete-signed-dispatch-qualification-v1-inspect','pg4154-final-recovery-abi-v1']


def main():
    os.umask(0o022)
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4156-final-failed-done-recovery-qualification-v1';out.mkdir()
    files={}
    for slot in SLOTS:
        raw=(W/slot/'manifest.safe.json').read_bytes();value=json.loads(raw)
        safe={k:v for k,v in value.items()if k not in {'host','localForward','command'}}
        safe['originalManifestSha256']=hashlib.sha256(raw).hexdigest()
        p=out/(slot+'.json');p.write_text(json.dumps(safe,ensure_ascii=False,indent=2)+'\n');files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    log=(W/'pg4154-final-recovery-abi-v1/host-abi.log').read_bytes();p=out/'host-abi.log';p.write_bytes(log);files[p.name]=hashlib.sha256(log).hexdigest()
    post=(W/'pg4150-failed-done-post-artifact-v1/manifest.safe.json').read_bytes();p=out/'prepared-post.json';p.write_bytes(post);files[p.name]=hashlib.sha256(post).hexdigest()
    value={'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'files':files,'designPR':'https://github.com/NakajimaMotoharu/schubert_NK_project/pull/133',
           'designMain':'ebde93b8c1b190fe7149d70f2991812a4110c9fd','recoveryIssued':False,
           'oldParentNormal':False,'formalAccepted':False,'productionPtAdded':0}
    p=out/'manifest.json';p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'results':len(SLOTS)}));return 0


if __name__=='__main__':raise SystemExit(main())
