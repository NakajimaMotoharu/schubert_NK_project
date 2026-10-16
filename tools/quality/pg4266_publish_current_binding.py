"""Publish bounded safe receipts only; never raw DB, native, argv, stacks or credentials."""
import datetime
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg4260_stable_admission_image import SOURCE

SLOT='PG4266-current-binding-image-v1'
SLOTS=['pg4240-typed-bom-fresh-noargs-once-v1','pg4246-fresh-current-live-binding-v1',
       'pg4250-current-admission-image-v1','pg4260-stable-admission-image-v1',
       'pg4262-current-acceptance-qualification-v1','pg4224-current-parent-stack-00']


def main():
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT
    out.mkdir();files={}
    for slot in SLOTS:
        raw=(W/slot/'manifest.safe.json').read_bytes();value=json.loads(raw)
        value['originalManifestSha256']=hashlib.sha256(raw).hexdigest()
        p=out/(slot+'.json');p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    p=out/'host-tests.log';p.write_bytes((W/'pg4262-current-acceptance-qualification-v1/host-tests.log').read_bytes());files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    result={'source':SOURCE,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,
            'rootStartedExactlyOnce':True,'genuineRootTerminalAccepted':False,'full24PostAccepted':False,'nativeGlobalAccepted':False,
            'rootTimeoutCauseProved':False,'formalAccepted':False,'productionPtAdded':0,'rawExported':False}
    p=out/'manifest.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
