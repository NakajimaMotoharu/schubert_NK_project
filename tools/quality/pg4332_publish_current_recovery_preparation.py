"""Safe same-current compile/inspect/qualification receipts only; no runtime authority inferred."""
import datetime
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg4260_stable_admission_image import SOURCE

SLOT='PG4332-current-recovery-preparation-v1'


def main():
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT;out.mkdir();files={}
    for slot in ['pg4310-current-actor-projection-v1','pg4312-current-failed-owned-tools-v1-compile','pg4316-current-failed-dispatch-v1-inspect',
                 'pg4322-current-post-profile-v1-compile','pg4330-current-recovery-qualification-v1']:
        raw=(W/slot/'manifest.safe.json').read_bytes();v=json.loads(raw);v['originalManifestSha256']=hashlib.sha256(raw).hexdigest()
        p=out/(slot+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    p=out/'host-tests.log';p.write_bytes((W/'pg4330-current-recovery-qualification-v1/host-tests.log').read_bytes());files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    v={'source':SOURCE,'designMain':'5086547c33aa61c94dbac02085dc34a23f94e15d','designPR':'https://github.com/NakajimaMotoharu/schubert_NK_project/pull/137',
      'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'operationsIssued':0,'recoveryAccepted':False,'parentNormal':False,
      'formalAccepted':False,'productionPtAdded':0,'rawExported':False}
    p=out/'manifest.json';p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
