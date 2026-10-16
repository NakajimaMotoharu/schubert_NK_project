"""Safe tool preparation and bounded parent measurements; no actual stop/native claims."""
import datetime
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W
from pg4260_stable_admission_image import SOURCE

SLOT='PG4292-current-owned-preparation-v1'


def main():
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT;out.mkdir();files={}
    for slot in ['pg4290-current-owned-qualification-v1','pg4224-current-parent-stack-03','pg4224-current-parent-stack-04']:
        raw=(W/slot/'manifest.safe.json').read_bytes();v=json.loads(raw);v['originalManifestSha256']=hashlib.sha256(raw).hexdigest()
        p=out/(slot+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    p=out/'host-tests.log';p.write_bytes((W/'pg4290-current-owned-qualification-v1/host-tests.log').read_bytes());files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    v={'source':SOURCE,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'actualABICompiled':False,
       'stopIssued':False,'independentPostAccepted':False,'rootTimeoutCauseProved':False,'formalAccepted':False,'productionPtAdded':0}
    p=out/'manifest.json';p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(p.read_bytes()).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
