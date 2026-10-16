"""Only allowlisted safe manifests/log; raw FD, DB, argv and private archives stay outside Git."""
import datetime
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]
SLOTS=['pg4160-retained-config-read-v1','pg4176-partial-tools-v1-proof',
       'pg4182-bounded-pool-tools-v1-stage','pg4182-bounded-pool-tools-v1-proof',
       'pg4190-partial-recovery-qualification-v1']


def main():
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4192-partial-recovery-qualification-v1';out.mkdir()
    hashes={}
    for slot in SLOTS:
        raw=(W/slot/'manifest.safe.json').read_bytes()
        value=json.loads(raw);value['originalManifestSha256']=hashlib.sha256(raw).hexdigest()
        p=out/(slot+'.json');p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    p=out/'host-tests.log';p.write_bytes((W/'pg4190-partial-recovery-qualification-v1/host-tests.log').read_bytes());hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    value={'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'files':hashes,'designMain':'9d300bd12881a2fae3a1b42654c10cc9eb105e47','designPR':'https://github.com/NakajimaMotoharu/schubert_NK_project/pull/134',
           'old4152Normal':False,'recoveryIssued':False,'formalAccepted':False,'productionPtAdded':0}
    p=out/'manifest.json';p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
    return 0


if __name__=='__main__':raise SystemExit(main())
