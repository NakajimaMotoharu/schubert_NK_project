"""Safe completed read/tool results only. Raw DB/FD/native/stacks never enter Git."""
import datetime
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg4222_fresh_current_noargs_once import SOURCE,DESIGN_MAIN

ROOT=Path(__file__).resolve().parents[2]
SLOTS=['pg4210-quiescent-current-read-v1','pg4212-quiescent-configuration-observation-v1',
       'pg4214-quiescent-ten-ref-observation-v1','pg4218-same-peer-observer-benchmark-v1',
       'pg4226-fresh-observer-qualification-v1','pg4230-final-fresh-observer-qualification-v1']


def main():
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4232-fresh-observer-qualification-v1';out.mkdir()
    files={}
    for slot in SLOTS:
        raw=(W/slot/'manifest.safe.json').read_bytes();value=json.loads(raw)
        value['originalManifestSha256']=hashlib.sha256(raw).hexdigest()
        p=out/(slot+'.json');p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    for name in ['complete.safe.json','host-tests.log']:
        p=out/name;p.write_bytes((W/'pg4230-final-fresh-observer-qualification-v1'/name).read_bytes());files[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    value={'source':SOURCE,'designMain':DESIGN_MAIN,'designPR':'https://github.com/NakajimaMotoharu/schubert_NK_project/pull/136',
           'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'rootStartIssued':False,
           'oldRoot143Normal':False,'formalAccepted':False,'productionPtAdded':0,'rootTimeoutCauseProved':False}
    p=out/'manifest.json';p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
